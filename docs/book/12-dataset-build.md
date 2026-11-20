# 第 12 章 数据集构建：从标记到可训练视图

前面所有环节都在"追加标记"。到了数据集构建这一步，要把这些标记兑现成一份**冻结的、可复现的、可被模型直接读的**训练集。这一章讲统一槽位向量、LeRobot v3 映射、QC 视图、manifest，以及评测集的固定与泄漏防护。

## 12.1 输入与步骤

[data-pipeline-design.md](../data-pipeline-design.md) §8：

- **输入**：策展决策（哪些 episode 处于 `training_ready`）、配方（`configs/mixtures/*.yaml`）、可选的查询快照、标注档案。
- **步骤**：可训练性检查 → 按配方采样 → 按档案组装标注 → 导出 LeRobot v3 与演示库切片 → 生成冻结的 manifest。

## 12.2 统一槽位向量

四轨数据的状态和动作维度各不相同。本仓库用固定布局的**槽位向量 + 二值有效掩码**统一它们（[data-format-contract.md](../data-format-contract.md) §2.3，`slot_layout_version = 1`），单位 SI，姿态用 3D 位置 + 6D 旋转：

| 段 | 维 | 内容 |
|---|---|---|
| `joint_pos` | 32 | 关节角，按具身档案顺序，不足补 0 + 掩码 |
| `ee_pose_left` / `ee_pose_right` | 9 + 9 | 末端位姿（相机系或基座系，`frame` 元数据声明） |
| `gripper_left` / `gripper_right` | 1 + 1 | 开度 [0,1] |
| `hand_left` / `hand_right` | 16 + 16 | 灵巧手关节 |
| `base_vel` | 3 | vx, vy, ωz |
| `head_pose` | 9 | 头部位姿（human/device 轨的相机自运动） |

合计 96 维。动作段同布局，以**相机系增量**为主。RDT 的 128 维与某大模型厂商的 80 维是同一思路。

**为什么用掩码而不是每具身一个头**：GR00T 式的每具身独立 MLP 头与"新增采集形态 = 新增 track 值不改 schema"的哲学冲突；掩码槽位更干净，新具身零架构改动（[training-pipeline.md](../training-pipeline.md) §1.3）。

**兼容视图**：同一数据集另导出 π0 兼容视图（原生维度 + 零填充到 32 维），让 M1 导出即可用 openpi 微调，这是 Stage A 的前提。

## 12.3 LeRobot v3 映射

LeRobot v3 一个数据集只有一个 `fps`。规则：**主表 fps = 动作/状态率**（robot 默认 100，device = 传感器原生率，human = 伪标签输出率，默认 30）；视觉流按原生 fps 存 mp4，取帧用最近帧并记录 Δt。

主要列：

| 列 | 说明 |
|---|---|
| `timestamp` / `fdp.timestamp_ns` | 秒（LeRobot 必需）/ 纳秒（无损，跨数据集对齐用） |
| `observation.images.<camera>` | 语义名；`fdp.image_dt_ns.<camera>` 记取帧 Δt |
| `observation.state` / `state_mask` | 槽位向量与掩码 |
| `action` / `action_mask` | 动作槽位与掩码 |
| `fdp.raw.<stream>` | 不进槽位的流原样带出（如触觉阵列） |
| `fdp.intervention` | 该帧处于人工接管中 |
| `fdp.subtask_index` | 子任务索引，−1 = 无 |
| `fdp.quality_score` | episode 级质量分 |

episode 级元数据全量 JSON 写进 `meta/episodes/*.parquet` 的 `fdp_meta` 列；子任务指令与区间在 `meta/fdp_subtasks.parquet`。

另有可选的**连续时间事件流视图**：每条消息一行 `(timestamp_ns, stream, values)`，不对齐到任何 fps。它是"schema 不预设消费架构"这一宣称的可验证形式（U-12）。

## 12.4 训练态加工

[curation-pipeline.md](../curation-pipeline.md) §5：

- **分辨率阶梯**：原始存档 / 训练 448p–720p / 预览 320p。GR00T 2 的经验是训练消费的是低分辨率、低帧率的连续窗口，存储要分层；按末端类型分档的分辨率与帧率是后续优化（行动清单 #8）。
- **归一化统计**：按（track × 具身）分开的分位数统计，1%/99% 截断归一化优于 min-max；统计文件随 `dataset_version` 走，**只在 QC 视图保留的样本上计算**。
- **增强不落盘**：颜色抖动、裁剪在 dataloader 做，存储永远保持原样。

## 12.5 QC 视图：标记不删除在训练态的落地

这是 2026-11-18 从 GR00T 2 回灌的关键机制（curation §5）：

- 各门的判定结果作为**列**追加到 episode / 步级指标表，**不改写原数据，也不在 dataloader 里实时过滤**。
- export 时按（数据集版本 × `quality_rule` 版本 × 训练配方的窗口长度）离线生成一份"合格样本起点"视图，写成 manifest 的一部分，连同该视图上算出的归一化统计一起进 lineage。
- 新增一个门 = 新增一列 + 重建视图，不重写已有列。

结果是：同一份数据可以同时存在多个视图，**消融只是换视图**。这就是第 8 章"阈值由消融裁决"在工程上可行的原因。

## 12.6 可训练性检查

export 前单独出报告，作为与完整性、有效性并列的独立质检维度：统一坐标系与单位、相机系→世界系变换约定、MANO 拓扑与关节定义一致、state/action 维度与槽位布局对齐、抽帧与编码规范、schema 与标注版本可追溯。**任何一项不过，该 episode 不进训练分片，只标记。**

## 12.7 分片、幂等与增量

- 分片按（track × 任务簇 × 质量层）组织，每 shard ≤2 GB parquet + 对应 mp4；`meta/fdp_shards.parquet` 记录每 shard 的 episode 与内容哈希。
- 幂等键：`(dataset_version, episode_id, content_hash)`。重跑时哈希一致的跳过，不一致的整 shard 重写并 bump `dataset_version`。
- 增量：新 episode 追加为新 shard，旧 shard 不改。
- writer 抽象成接口（`ExportWriter`），LeRobot v3 是默认实现，对 `lerobot` 核心包的依赖限定在该实现内（R-10）。

## 12.8 manifest

冻结的 manifest 包含：episode 清单与内容哈希、配方哈希、查询快照哈希、标注档案与规范版本、`split_version`、合成数据占比、QC 视图。它对应 lineage 的 `datasets` / `dataset_episodes` 表。

有了 manifest，"这个模型是用什么数据训出来的"就有了唯一答案。

## 12.9 评测集固定与泄漏防护

[curation-pipeline.md](../curation-pipeline.md) §8：

- **held-out 在 ingest 后、curation 前就固定**：按 `scene_id` 与 `operator_id` 做组切分（同一场景、同一操作者不跨 train/held-out），比例 5–10%，写入 `split` 并版本化；**曾进入 held-out 的 episode 永不回流训练集**。
- M1 期 curation 还没实现时，export 层用同一组规则生成 held-out 清单文件——机制不等 M2。
- 去重与再平衡只在 train 池内做；演示库切片不得取自 held-out；合成种子不得取自 held-out。
- **泄漏检测**：训练前跑 train↔held-out 的近重复检查（余弦 >0.95 视为泄漏，从 train 剔除并记录）。

为什么要在 curation 之前固定？因为如果先策展再切分，再平衡的聚类统计就已经"看过"了评测集，评测结果会系统性偏高。

## 12.10 本章小结

- 96 维槽位 + 掩码统一四轨；同时出 π0 兼容视图。
- 主表 fps = 动作率，视觉按原生率，取帧记 Δt。
- QC 视图：判定是列，视图离线生成，消融只是换视图。
- 可训练性检查不过只标记、不进分片。
- manifest 钉住数据、配方、查询、标注版本、切分版本。
- held-out 入湖即固定、组切分、永不回流，训练前查泄漏。

**延伸阅读**：[data-format-contract.md](../data-format-contract.md) §2 · [curation-pipeline.md](../curation-pipeline.md) §5、§8 · [data-pipeline-design.md](../data-pipeline-design.md) §8 · [research-gr00t2.md](../research-gr00t2.md) §4.7
