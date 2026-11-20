# 第 7 章 入湖：校验、对齐、转码、幂等

入湖（ingest）把上传完成的原始文件变成 `state = ingested` 的 episode：raw 区对象、元数据库记录、AV1 转码产物（[ingest-spec.md](../ingest-spec.md)）。它是第一道"确定性"关口——没有任何模型参与，只做物理上能判定的事。

## 7.1 流水线

```
uploaded ──校验──► verified ──拆流/对齐──► aligned ──转码──► transcoded ──登记──► ingested
   └─(哈希不符/损坏)→ rejected(reject_corrupt)   └─(对齐超预算)→ ingested + flag:sync_budget_exceeded
```

每一步幂等、每一步产物写 `artifacts` 表、任一步失败进重试。

## 7.2 校验

- **完整性**：分片哈希 vs 上传声明；全文件 BLAKE3 → `content_hash`；MCAP chunk CRC 全量校验；缺尾部索引 → 线性扫描恢复并标 `flag:recovered_index`。
- **元数据**：`/meta/episode` 必须存在；human 轨缺 `consent_ref` / `region`、各轨缺 `device_id` / `calibration_ref` / `operator_id` → `reject_meta`。
- **标定**：标定版本必须存在于 `devices` 表且与固件兼容；否则 `flag:calib_unknown`——不拒收，但不进 robot/device 训练分片。
- **时长**：<10 s → `reject_short`。
- **时间戳单调**：任一流倒退 >1 ms → `reject_timing`。GoPro 类设备已知有抖动，先用 50 条实测分布、阈值取 P99，写进 `configs/ingest/thresholds.yaml`（R-07）。

注意"拒收"和"标记"的区别：拒收只用于**物理上无法使用**（损坏、缺授权、时间倒退）；能用但不适合某种用途的，一律标记。

## 7.3 拆流与对齐

- 非 MCAP 输入（MP4 + GoPro 遥测、手机 App 的 JSON 遥测）拆成标准 topic 写成 MCAP，原文件同样存 raw 区。
- 视频帧时间取曝光中点；跨时钟域偏移按第 5 章的方法估计，写 `clock_domains[]`，残差进 QC。
- **丢帧**：帧间隔 >1.5/fps 记丢帧；丢帧率 >2% 标 `flag:frame_drop`，>10% `reject_frame_drop`；信号流缺口 >100 ms 标 `flag:signal_gap`。
- **不重采样**：所有流保留原生时间戳。

## 7.4 转码

- 存档：AV1（svt-av1，硬编优先）、`yuv420p`、CRF 30、先用 1 s 固定 GOP（ingest 时还不知道子任务边界；分割后按需重切 GOP 是可选优化）。
- 训练分辨率阶梯（448p / 720p）与预览流在 curation 打包时生成，不在 ingest 做。
- **raw 原编码文件永久保留。**

GOP 长度最终要跟着消费方式调：世界-动作模型的长序列可用大 GOP，VLA 的短窗口需要小 GOP（Dyna 的经验 ⚠️）。所以 GOP 是 export 参数，不是存档常量。

## 7.5 重试、退避与死信

| 错误类型 | 例子 | 处置 |
|---|---|---|
| 可重试 | 存储超时、GPU 池满、VLM API 限流 | 指数退避 1→2→4→8→16 分钟，最多 5 次，之后进死信队列并告警 |
| 不可重试 | 哈希不符、schema 无法迁移、损坏无法恢复 | 直接 `rejected`，通知上传方（App 显示原因，可重传） |
| 部分成功 | 转码失败但校验/对齐成功 | 保留 `aligned`，只重跑转码 |

## 7.6 幂等与增量重跑

- **幂等键**：`(episode_id, content_hash, ingest_version)`。同键重复触发直接返回已有结果。
- `ingest_version` 随对齐算法、阈值、转码参数变化而 bump（`configs/ingest/*.yaml` 的哈希）。bump 后可对历史 episode **增量重跑**：只重跑受影响的步骤；旧产物保留到新产物验证通过后再标过期。
- 重跑不改 `episode_id`，只写 `artifacts` 与 `decisions` 的新行。

幂等是可重放的前提，可重放是"阈值可消融"的前提。如果重跑一次 ingest 会产生新的 episode_id，那么 lineage 就断了，任何"换一组阈值再试"的实验都无法和旧结果对比。

## 7.7 断点续传

- 上传分片 8 MB，每片带哈希；服务端记录已收分片集合；客户端可从任意分片续传；整文件哈希通过才触发 ingest。
- 多 part 的 episode 要所有 part 到齐才进 ingest；超过 24 小时未到齐，标 `flag:incomplete_parts` 并以已到 part 入湖——**不等永远**。
- **预览流先行**：320p 预览流先上传、先跑技术门 + 视觉门快筛，不通过则通知 App 停止上传存档流。对众包来说这一条省下的带宽相当可观。

## 7.8 采集规则快照绑定

这是 2026-11-17 对照某大模型厂商链路后新增的一条（[data-pipeline-design.md](../data-pipeline-design.md) §3）：每个采集任务下发时冻结两份规则文件，并把哈希写进该任务下每条 episode 的元数据。

- `collection_rule`：标准步骤序列、允许的物体与场景、必需的流和相机。质检的流程指标（步骤覆盖率、顺序匹配率）和打标的边界先验都从这里读。
- `quality_rule`：该任务适用的质检阈值版本与状态机。

目的：**规则改了，旧结论仍能对应到当时的规则。** 否则半年后有人问"这批数据当时为什么判 pass"，没人答得上来。提议位置 `configs/qc/collection_rules/<task>.yaml`、`configs/qc/quality_rules/<version>.yaml`，改动 = 新版本，哈希字段随契约 0.3 入 schema。

## 7.9 验收

- 单测：损坏 MCAP 恢复、合成数据已知偏移的时钟估计、丢帧统计、幂等重入。
- golden fixture：一条 10 s 合成 episode（三路流 + 已知偏移），输出与预期元数据比对。
- H0 首批 100 小时数据 ingest 通过率 ≥90%，被拒原因分布可解释。

## 7.10 本章小结

- ingest 只做确定性的事：校验、拆流、对齐（只产元数据）、转码、登记。
- 拒收只给物理上不可用的；其余标记。
- 幂等键 + 版本化配置 = 可增量重跑 = 阈值可消融。
- 采集规则快照让质检结论可复现。

**延伸阅读**：[ingest-spec.md](../ingest-spec.md) · [data-pipeline-design.md](../data-pipeline-design.md) §3 · [recorder-sync-and-storage.md](../recorder-sync-and-storage.md) §4
