# ingest 规范：校验 · 对齐 · 转码 · 重试 · 幂等 · 断点续传

> 2026-09-08。M1 交付物 `fdp ingest` 的行为规范。输入：上传完成的 raw 文件（MCAP，或 P0 手机/GoPro 的 MP4 + 遥测）；输出：`state = ingested` 的 episode、raw 区对象、元数据库记录、AV1 转码产物。时间语义与误差预算见 architecture §8，格式见 data-format-contract。

## 1. 流水线与状态

```
uploaded ──校验──► verified ──拆流/对齐──► aligned ──转码──► transcoded ──登记──► ingested
   └─(哈希不符/损坏)→ rejected(reject_corrupt)   └─(对齐超预算)→ ingested + flag:sync_budget_exceeded
```

每步幂等（§5），每步产物写 `artifacts` 表；任一步失败进重试（§4）。

## 2. 校验

- 分片哈希 vs 上传声明；全文件 BLAKE3 → `content_hash`；MCAP chunk CRC 全量校验；缺尾部索引 → 线性扫描恢复并标 `flag:recovered_index`。
- 元数据完整：`/meta/episode` 存在；`consent_ref`/`region`（human）、`device_id`/`calibration_ref`（human/device/robot）、`operator_id`（robot/device）缺失 → `reject_meta`。
- 标定版本存在于 `devices` 表且与 `firmware_version` 兼容；否则 `flag:calib_unknown`（不拒收，但不进 robot/device 训练分片）。
- 时长 <10 s → `reject_short`；`duration_ns` 缺失 → 从最后一条消息补并标 `flag:abnormal_end`。
- 时间戳单调性：任一流出现倒退 >1 ms → `reject_timing`；GoPro 类设备已知抖动先在 H0 用 50 条实测分布，阈值取 P99（governance R-07），写入 `configs/ingest/thresholds.yaml`。

## 3. 拆流与对齐

- 非 MCAP 输入（MP4 + GoPro 遥测 / 手机 App 的 JSON 遥测）拆成 `/video/*`、`/imu/*`、`/signal/*` 写成标准 MCAP，原文件同样存 raw 区。
- 视频帧 `publish_time` 取曝光中点；无曝光信息的设备用 `pts − 0.5/fps` 近似并标 `flag:pts_approx`。
- 跨时钟域：有 `/event/sync` 的用同步事件估计偏移 + 线性漂移；无同步事件的多设备会话用 IMU 角速度 vs 视觉旋转互相关（窗口 30 s，搜索 ±500 ms）估计偏移；结果写 `clock_domains[]`，残差进 QC。
- 对齐残差检查（architecture §8.4 预算）：视觉↔IMU ≤2 ms、视觉↔动作 ≤5 ms（robot/device）/ ≤15 ms（human）；超预算标 `flag:sync_budget_exceeded`。
- 丢帧：视频帧间隔 >1.5/fps 记为丢帧，丢帧率 >2% 标 `flag:frame_drop`，>10% `reject_frame_drop`；信号流缺口 >100 ms 标 `flag:signal_gap`。
- **不重采样**：所有流保留原生时间戳；对齐只产生偏移与残差元数据，不改数据。

## 4. 重试、退避与死信

- 可重试错误（存储超时、GPU 池满、VLM API 限流）：指数退避 1 → 2 → 4 → 8 → 16 分钟，最多 5 次；之后进死信队列并告警（data-platform §4）。
- 不可重试错误（哈希不符、schema 无法迁移、损坏无法恢复）：直接 `rejected` 并通知上传方（App 显示原因，Creator 可重传）。
- 部分成功：转码失败但校验/对齐成功 → 保留 `aligned` 状态，只重跑转码步。

## 5. 幂等键与增量重跑

- 幂等键：`(episode_id, content_hash, ingest_version)`；同键重复触发直接返回已有结果。
- `ingest_version` 随对齐算法/阈值/转码参数变化而 bump（`configs/ingest/*.yaml` 哈希）；bump 后可对历史 episode **增量重跑**：只重跑受影响步骤（如仅转码参数变了，不重跑对齐），旧产物保留到新产物验证通过后再标记过期（不删 raw）。
- 重跑不改 `episode_id`，改 `artifacts` 与 `decisions` 的新行。

## 6. 断点续传语义

- 上传：分片 8 MB，每片带哈希；服务端记录已收分片集合；客户端可从任意分片续传；整文件哈希校验通过才触发 ingest。
- 多 part 文件（data-format-contract §1.1）的 episode：所有 part 到齐才进入 ingest；超过 24 小时未到齐标 `flag:incomplete_parts` 并以已到 part 入湖（不等永远）。
- 预览流先行：320p 预览流上传后即跑技术门 + 视觉门快筛（curation §1.1–1.2 的子集），不通过则通知 App 停止上传存档流（省带宽，index-replica-plan §2）。

## 7. 转码

- 存档：AV1（svt-av1，硬编优先）、`yuv420p`、CRF 30、GOP 对齐子任务边界附近（ingest 期未知子任务，先用 1 s 固定 GOP；curation 分割后按需重切 GOP 是可选优化）。
- 训练分辨率阶梯（448p/720p）与预览流由 curation 打包时生成，不在 ingest 做。
- 转码产物哈希进 `artifacts`；raw 原编码文件永久保留（raw 永存）。

## 8. 交付与测试

- 单测：损坏 MCAP 恢复、时钟偏移估计（合成数据已知偏移）、丢帧统计、幂等重入。
- golden fixture：`tests/fixtures/` 放一条 10 s 合成 episode（三路流 + 已知偏移），ingest 输出与预期元数据比对。
- 验收：H0 首批 100 小时数据 ingest 通过率 ≥90%，被拒原因分布可解释。
