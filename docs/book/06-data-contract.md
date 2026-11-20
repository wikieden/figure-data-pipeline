# 第 6 章 数据契约：MCAP、EpisodeMeta 与版本迁移

数据契约是 M1 的核心交付规范（[data-format-contract.md](../data-format-contract.md)）。它定死三件事：机上和原始 MCAP 文件长什么样；EpisodeMeta 每个字段的含义、谁写、何时写；如何映射到训练态。代码 `src/fdp/schema.py` 是契约的实现，**改字段先改契约文档，再改代码**。

## 6.1 MCAP 采集态

### 文件与分段

- 一个 episode = 一个或多个文件 `<episode_id>.part-<n>.mcap`，单文件上限 2 GB 或 10 分钟。
- 写入参数：chunk 4 MB、zstd level 3、每 chunk 带 CRC，索引在文件尾。
- 目录：`data/raw/<track>/<date>/<session_id>/<episode_id>.part-<n>.mcap`。
- **入湖态按读取模式分组 topic**：视觉流一组、本体感知 + 动作一组，各组时间主序写入、组间不共 chunk。这是 Dyna 在百万小时规模上验证过的做法 ⚠️，与分层采样率决策天然一致。

### topic 命名

| topic | 频率 | 说明 |
|---|---|---|
| `/video/<camera>` | 10–60 Hz | 机上 h264/h265 Annex-B，入湖后 AV1；关键帧间隔 ≤1 s；`<camera>` 用语义名 |
| `/signal/<stream>` | 50–1000 Hz | `values: float32[dim]` |
| `/imu/<device>` | ≥200 Hz | 加速度 + 角速度 + 温度 |
| `/event/intervention` | 稀疏 | 接管开始/结束 |
| `/event/task` | 稀疏 | 任务开始/结束/中止、口令、子任务标记 |
| `/event/sync` | 稀疏 | 跨设备同步事件 |
| `/meta/episode` | 文件头 1 次 + 结束 1 次 | 结束那份含 `duration_ns` |
| `/meta/calibration` | 1 次 | 内外参、时间偏移、`calibration_ref` |
| `/meta/health` | 1 Hz | 自检、丢帧计数、磁盘余量 |

### 相机语义名归一化

设备上任意命名，export 时映射到固定词表：`head`、`head_left/right`、`wrist_left/right`、`palm_left/right`、`ego`、`ego_wrist`、`third_person`、`slam_left/right`。映射表随设备档案走。

这条看似琐碎，实则致命。SmolVLA 的教训：相机命名不一致会**静默**毁掉跨数据集训练——模型不会报错，只是把左腕当成右腕学。

## 6.2 EpisodeMeta：一张表管四条轨

EpisodeMeta（schema 0.2）是四轨共用的元数据。按"谁写"分五类写入者：REC（recorder）、ING（ingest）、CUR（curation）、EXP（export）、RT（运行时回流）。几组关键字段：

**身份与来源**

| 字段 | 写入者 | 说明 |
|---|---|---|
| `episode_id` | REC | ULID，全局唯一 |
| `session_id` | REC | 同一次佩戴或开机 |
| `track` | REC | robot / human / device / sim |
| `source` | REC | sim 子来源，或 robot 回流的 `fleet` |
| `robot_model` / `device_id` / `operator_id` | REC | 具身档案、设备档案、采集者 |
| `calibration_ref` / `firmware_version` | REC | 标定哈希、固件版本 |
| `parent_episode_id` | CUR | 派生产物（转换、合成、增殖）指向原始 |

**时间**

| 字段 | 说明 |
|---|---|
| `started_at_ns` | UTC ns |
| `duration_ns` | 结束时写；缺失由 ING 补并标 `flag:abnormal_end` |
| `clock_domains` | 多设备必填：`name, offset_to_utc_ns, drift_ppm` |

**状态与质量**

| 字段 | 说明 |
|---|---|
| `state` | 状态机：raw → ingested → gated → scored → segmented → labeled → training_ready；`rejected` 终态 |
| `quality_flags` | `reject_*` / `flag:*`，标记不删除 |
| `quality_score` | [0,1]；human 轨为伪标签质量分 |
| `success` / `intervention_ts_ns` | 成败与接管时刻 |

**切分、存储与合规**

| 字段 | 说明 |
|---|---|
| `scene_id` | 场地标识，held-out 组切分键 |
| `split` / `split_version` | train / held_out |
| `storage_uri` / `content_hash` / `size_bytes` | raw 位置、BLAKE3 合并哈希 |
| `consent_ref` / `region` | human 轨必填；决定驻留与合规开关 |
| `policy_version` / `deployment_id` | 回流 episode 必填 |

**标注**

| 字段 | 说明 |
|---|---|
| `task_instruction` | 任务级；VLM 标注可覆盖并保留原值到 lineage |
| `subtasks` | `instruction, start_ns, end_ns` |
| `environment_tags` / `object_tags` | 再平衡与多样性计数 |

**一条容易被忽视的规则**：未在契约里的键，读侧忽略（前向兼容），写侧禁止（`extra="forbid"` 只对写路径开启）。这同时保证了"旧代码能读新数据"和"新代码不会偷偷写出未登记字段"。

## 6.3 版本迁移

- `schema_version` 用 `major.minor`。minor 升级只允许**新增可选字段或放宽约束**，必须能无损读旧数据；major 升级允许删字段，但要提供迁移函数并保留旧 reader 一个里程碑周期。
- **迁移在读侧完成**（`fdp.schema.migrate(raw) -> EpisodeMeta`），MCAP 文件本身不回写；ingest 把迁移后的元数据另存进元数据库，raw 永远保留原版本。
- 0.1 → 0.2：`subtask_instructions` 复制到 `subtasks`（区间为 None）；`state` 由 `curated` 推断；其余新增字段取空。
- 冻结样本 `tests/fixtures/episode_v0_1.json` 必须永远可读（`tests/test_schema.py::test_migrate_v0_1`）。

这是本仓库目前**已经实现**的部分。

## 6.4 契约 0.3 待入项

随着设计推进，一批字段已经确定要加、但还没进 schema（data-format-contract §3.1）。列在这里，因为它们揭示了数据层下一步要表达什么：

| 待入项 | 为什么 |
|---|---|
| 子任务槽位化字段：`hand`、`outcome`、`contact`、`keyframe_ns`、结构化描述槽位、`boundary_basis` | 标注不再是一句自由文本（第 9 章）；现在采集时几乎不费事，以后补标代价很高 |
| `grasp_aperture` | human 轨伪动作的连续抓取信号，与 device 轨 `gripper_width` 同义 |
| 连续帧对导出（`frame_pair_stride`） | 世界-动作模型目标需要 (t, t+Δ) 帧对 |
| 采集端事件下传 | 失败、重拍、换道具、中止要随片段送到标注端 |
| human 轨估计内参与 `camera_fov` | 众包设备没有出厂标定 |
| 奖励列：`reward.outcome`、`reward.progress`、`reward.rubric.<name>` | 奖励标注与语言标注同源，喂 RL 和评测；每列记来源（model / predicate / human）与版本 |
| 力类动作槽位：`ee_wrench_target`、`stiffness` | 触觉与力开始进入动作空间 |
| 采集规则哈希（`collection_rule`、`quality_rule`） | 质检结论可复现（第 7 章） |
| TIS2 末端档案扩展 | 两节同构手的关节、命令来源、掌心视图 |

## 6.5 本章小结

- MCAP 采集态：多 part、chunk 带 CRC、按读取模式分组 topic、语义化相机名。
- EpisodeMeta 一张表管四轨，按写入者分工；读侧宽容、写侧严格。
- 迁移在读侧做，raw 不回写，冻结样本永远可读。
- 0.3 待入项指向三个方向：标注结构化、奖励与力进入数据、质检可复现。

训练态（LeRobot v3）的映射放在第 12 章讲，因为它依赖策展的产物。

**延伸阅读**：[data-format-contract.md](../data-format-contract.md) · `src/fdp/schema.py` · [data-strategy-roadmap.md](../data-strategy-roadmap.md) §7.2
