# 数据格式契约：MCAP 采集态 · EpisodeMeta · LeRobotDataset v3 训练态

> 2026-09-08。M1 的核心交付规范。三件事在此定死：(1) 机上/原始 MCAP 文件长什么样；(2) EpisodeMeta 每个字段的含义、谁写、何时写；(3) 如何映射到 LeRobotDataset v3。代码 `src/fdp/schema.py` 是本契约的实现，**改字段先改本文再改代码**（CLAUDE.md 约定）。时间语义见 [architecture.md](architecture.md) §8。

## 1. MCAP 采集态

### 1.1 文件与分段

- 一个 episode = 一个或多个 MCAP 文件（`<episode_id>.part-<n>.mcap`），单文件上限 2 GB 或 10 分钟，先到为准；分段切换时写入 `/meta/segment` 消息记录续接关系。session 级信息（操作员、设备、标定）在每个文件头重复写一份，任一文件可独立解析。
- 写入参数：chunk 大小 4 MB、压缩 zstd（level 3）、每个 chunk 带 CRC、chunk 索引与消息索引在文件尾（recorder 崩溃时尾部缺失，ingest 走线性扫描恢复，见 [recorder-sync-and-storage.md](recorder-sync-and-storage.md) §3）。
- 文件名与目录：`data/raw/<track>/<date>/<session_id>/<episode_id>.part-<n>.mcap`。

**外部验证（2026-09-14）**：Dyna 在百万小时规模上把 episode 容器从 H5 逐帧 JPEG 换成 canonical MCAP + H.264，并按训练样本的读取模式把 topic 分组（相机流一组、本体感知 + 动作一组），各组时间主序写入、组间不共 chunk（topic-group chunking）：存储 −68%、样本读延迟 2.9×、chunk 抓取 3.4× 更少；GOP 按消费模式调（WAM 长序列可用大 GOP，VLA 短窗口需小 GOP）（[research-dyna-comparison.md](research-dyna-comparison.md) §2.3）。本节 chunk 规则据此补一条：**入湖态 MCAP 写出时按读取模式分组 topic，视觉流与信号流不共 chunk，组内时间主序**；这与决策 3 的分层采样率天然一致；chunk 时长与训练态抽帧步长对齐（U-12 验证钩子），GOP 长度作为 export 参数随消费目标（next_action / +next_frame）切换。

### 1.2 Channel / topic 命名

| topic | schema 名 | 消息编码 | 频率 | 说明 |
|---|---|---|---|---|
| `/video/<camera>` | `fdp.CompressedVideo`（兼容 foxglove.CompressedVideo 字段） | 二进制 h264/h265 Annex-B（机上）；入湖后 AV1 OBU | 10–60 Hz | `<camera>` 用语义名（§2.2）；关键帧间隔 ≤1 s |
| `/signal/<stream>` | `fdp.Signal` | JSON（M1）；protobuf 可选（M2 后） | 50–1000 Hz | `values: float32[dim]`；`stream` 与 `SignalStream.name` 一致 |
| `/imu/<device>` | `fdp.Imu` | JSON | ≥200 Hz | 加速度 + 角速度 + 温度 |
| `/event/intervention` | `fdp.Event` | JSON | 稀疏 | 接管开始/结束，见 [robot-track-teleop.md](robot-track-teleop.md) §4 |
| `/event/task` | `fdp.Event` | JSON | 稀疏 | 任务开始/结束/中止、操作员口令、子任务标记 |
| `/event/sync` | `fdp.Event` | JSON | 稀疏 | 跨设备同步事件（LED/拍手），architecture §8.3 |
| `/meta/episode` | `fdp.EpisodeMeta` | JSON | 1 次（文件头）+ 结束时 1 次 | 结束时的一份含 `duration_ns`；缺失=非正常结束 |
| `/meta/calibration` | `fdp.Calibration` | JSON | 1 次 | 内参/外参/时间偏移，含 `calibration_ref` 哈希 |
| `/meta/health` | `fdp.Health` | JSON | 1 Hz | 传感器自检、丢帧计数、磁盘余量 |

每条消息 `publish_time` = 采样时刻（ns，单调时钟），`log_time` = 写入时刻；对齐只用 `publish_time`（architecture §8.1）。

### 1.3 各轨最小流集合

| track | 必须 | 可选 |
|---|---|---|
| robot | ≥1 路 `/video/head*`、`/signal/joint_pos`、`/signal/joint_vel`、`/signal/action`（遥操作指令）、`/event/intervention`、`/event/task` | `/video/wrist_*`、`/video/palm_*`、`/signal/tactile_*`、`/signal/ee_pose`、`/signal/base_vel` |
| human | ≥1 路 `/video/ego`、`/imu/head`（有 IMU 时） | `/video/slam_left|right`、`/signal/audio_env`、`/event/task`（口令）；Creator App 手机众包另带 `/meta/task_goal`（个性化任务的谓词目标 id + 场景孪生版本，index-replica-plan §2） |
| device | `/video/ego_wrist`（UMI 鱼眼）、`/signal/ee_pose`（原生频率 ≥50 Hz）、`/signal/gripper_width`、`/imu/wrist` | `/video/ego`（头戴场景）、`/signal/glove_joint_*`（穿戴子形态） |
| sim | `/video/*`（渲染）、`/signal/joint_pos`、`/signal/action`、`/meta/sim`（仿真器/资产/随机化种子） | 特权信息 `/signal/object_pose_*`、`/signal/contact_*` |

缺失的可选流在 EpisodeMeta 中不出现即可；训练侧用掩码表达（决策 2 可空模态）。

## 2. LeRobotDataset v3 训练态映射

### 2.1 表结构

LeRobot v3 一个数据集只有一个 `fps`。我们的规则：**主表 fps = 该数据集的动作/状态率**（robot 轨默认 100，device 轨 = 传感器原生率，human 轨 = 伪标签输出率，默认 30），视觉流按原生 fps 存 mp4，取帧用最近帧并记录 Δt——即 curation-pipeline §5 的取帧规则在 export 层的实现。

| 列 | 类型 | 来源 | 说明 |
|---|---|---|---|
| `timestamp` | float32 s | `publish_time` − episode 起点 | LeRobot 必需 |
| `fdp.timestamp_ns` | int64 | 同上，ns | 无损；跨数据集对齐用 |
| `frame_index` / `episode_index` / `index` / `task_index` | int64 | export 生成 | LeRobot 必需 |
| `observation.images.<camera>` | video | `/video/<camera>` | 语义名见 §2.2；`fdp.image_dt_ns.<camera>` 记录取帧 Δt |
| `observation.state` | float32[S] | 槽位向量（§2.3） | 统一视图 |
| `observation.state_mask` | bool[S] | 槽位有效掩码 | 统一视图 |
| `action` | float32[A] | 槽位向量（动作段） | 统一视图 |
| `action_mask` | bool[A] | | |
| `fdp.raw.<stream>` | float32[dim] | 原生流 | 不进槽位的流原样带出（如触觉阵列） |
| `fdp.intervention` | bool | `/event/intervention` 展开 | 该帧处于人工接管中 |
| `fdp.subtask_index` | int16 | `subtasks[]` 时间区间 | −1 = 无 |
| `fdp.quality_score` | float32 | EpisodeMeta | episode 级，每帧重复 |

episode 级元数据（`EpisodeMeta` 全量 JSON）写入 `meta/episodes/*.parquet` 的 `fdp_meta` 列；`meta/tasks` 存任务级指令；子任务指令与区间在 `meta/fdp_subtasks.parquet`。

### 2.2 相机语义名归一化

设备上任意命名，export 时映射到固定词表：`head`、`head_left`、`head_right`、`wrist_left`、`wrist_right`、`palm_left`、`palm_right`、`ego`（头戴第一视角）、`ego_wrist`（UMI 腕装）、`third_person`、`slam_left`、`slam_right`。映射表随设备档案走（`device_id` → camera map）。SmolVLA 的教训（research-vla-pretraining §1.6）：相机命名不一致会静默毁掉跨数据集训练。

### 2.3 统一槽位向量

固定布局（版本 `slot_layout_version = 1`），单位 SI，姿态用 3D 位置 + 6D 旋转表示：

| 段 | 维 | 内容 |
|---|---|---|
| `joint_pos` | 32 | 关节角，按具身档案顺序，不足补 0 + 掩码 |
| `ee_pose_left` / `ee_pose_right` | 9 + 9 | 末端位姿（相机系或基座系，`frame` 元数据声明） |
| `gripper_left` / `gripper_right` | 1 + 1 | 开度 [0,1] |
| `hand_left` / `hand_right` | 16 + 16 | 灵巧手关节（三指/五指都放得下；布局细节等 governance U-04 裁决后冻结） |
| `base_vel` | 3 | vx, vy, ωz |
| `head_pose` | 9 | 头部位姿（human/device 轨的相机自运动） |

合计 96 维；动作段同布局（增量形式，相机系为主，training-pipeline §1.2-4）。`SignalStream.slot` 声明流落到哪一段。**π0 兼容视图**：同一数据集另导出 `observation.state`/`action` 为原生维度 + 零填充到 32 维（openpi 默认），关节顺序按具身档案。

### 2.4 分片、幂等与增量

- 分片按（track × 任务簇 × 质量层）组织，每 shard ≤ 2 GB parquet + 对应 mp4；`meta/fdp_shards.parquet` 记录每 shard 包含的 episode 与内容哈希。
- 幂等键：`(dataset_version, episode_id, content_hash)`；重跑 export 时已存在且哈希一致的 episode 跳过，不一致的整 shard 重写并 bump `dataset_version`。
- 增量：新 episode 追加为新 shard，旧 shard 不改；held-out 清单（curation §8）作为 export 输入，held-out episode 单独成 split。
- 归一化统计（分位数 1%/99%）按（track × 具身）分开存 `meta/stats/<track>_<embodiment>.json`，随 `dataset_version` 走。
- writer 抽象成接口（`ExportWriter`），LeRobot v3 是默认实现；对 `lerobot` 核心包（≥0.6；`lerobot-dataset` 独立包已停更，2026-09-09 改判 U-03）的依赖限定在该实现内（governance R-10）。

### 2.5 连续时间消费视图（governance U-12 的验证钩子）

除主表外可选导出"事件流"视图：每条消息一行 `(timestamp_ns, stream, values)`，不对齐到任何 fps。这是"schema 不预设消费架构"宣称的可验证形式；M1 出一个测试用最小导出，证明可从同一 MCAP 生成两种视图。

## 3. EpisodeMeta 字段契约（schema 0.2）

写入者缩写：REC recorder、ING ingest、CUR curation、EXP export、RT 运行时回流。

| 字段 | 类型 | 写入者 | 必填 | 说明 |
|---|---|---|---|---|
| `schema_version` | str | REC | ✓ | `"0.2"`；读侧按 §4 迁移 |
| `episode_id` | str | REC | ✓ | ULID；全局唯一 |
| `session_id` | str \| None | REC | robot/device/human ✓ | 同一次佩戴/开机 |
| `track` | Track | REC | ✓ | robot / human / device / sim |
| `source` | str \| None | REC | sim ✓ | sim 子来源：`teleop_replay` / `dexmimicgen` / `neural_trajectory` / `mocap_retarget` / `rl_rollout`；robot 轨回流用 `fleet` |
| `robot_model` | str \| None | REC | robot/sim ✓ | 具身档案 id |
| `operator_id` | str \| None | REC | robot/device ✓；human 用 Creator id | 质量归因、消融切分 |
| `device_id` | str \| None | REC | human/device ✓ | 设备档案 id → 相机映射、标定 |
| `calibration_ref` | str \| None | REC | human/device/robot ✓ | 标定文件哈希 |
| `firmware_version` | str \| None | REC | 自研设备 ✓ | |
| `started_at_ns` | int | REC | ✓ | UTC ns |
| `duration_ns` | int | REC/ING | ✓ | 结束时写；缺失由 ING 从最后一条消息补并标 `flag:abnormal_end` |
| `clock_domains` | list[ClockDomain] | REC/ING | 多设备 ✓ | `name, offset_to_utc_ns, drift_ppm` |
| `videos` / `signals` | list | REC | ✓ | 流声明；`rate_hz` 如实填 |
| `scene_id` | str \| None | REC/CUR | ✓（H0 起） | 场地/房间标识，held-out 组切分键 |
| `environment_tags` / `object_tags` | list[str] | CUR | | 再平衡与多样性 KPI 计数 |
| `task_instruction` | str \| None | REC/CUR | | 任务级；CUR 的 VLM 标注可覆盖并保留原值到 lineage |
| `subtask_instructions` | list[str] | CUR | | 0.1 遗留；0.2 起以 `subtasks` 为准 |
| `subtasks` | list[Subtask] | CUR | | `instruction, start_ns, end_ns` |
| `state` | EpisodeState | ING/CUR | ✓ | 状态机：raw → ingested → gated → scored → segmented → labeled → training_ready；`rejected` 终态 |
| `quality_flags` | list[str] | CUR | | `reject_*` / `flag:*`；标记不删除 |
| `quality_score` | float \| None | CUR | | [0,1]；human 轨为伪标签质量分 |
| `curated` | bool | CUR | | 等价于 `state == training_ready`；保留兼容 |
| `success` | bool \| None | REC/CUR | | robot/device/sim |
| `intervention_ts_ns` | list[int] | REC | | 接管时刻（robot-track-teleop §4） |
| `split` / `split_version` | str \| None | ING/EXP | | `train` / `held_out`；curation §8 |
| `storage_uri` | str \| None | ING | ✓ | raw 对象存储路径 |
| `content_hash` | str \| None | ING | ✓ | 全部 part 文件的 BLAKE3 合并哈希 |
| `size_bytes` | int \| None | ING | ✓ | |
| `consent_ref` | str \| None | REC/ING | human ✓ | Creator 协议版本 + 同意记录 id |
| `region` | str \| None | REC/ING | human ✓ | ISO 3166 国家/地区，决定驻留与合规开关 |
| `policy_version` / `deployment_id` | str \| None | RT | 回流 ✓ | 车队回流 episode 来自哪个策略与部署 |
| `parent_episode_id` | str \| None | CUR | 派生产物 ✓ | 具身转换等派生 episode 指向原始 |

未在表中的键：读侧忽略（前向兼容），写侧禁止（`extra="forbid"` 只对写路径开启）。

### 3.1 契约 0.3 待入项（2026-09-14 增补）

- **`grasp_aperture`**（human 轨伪动作，浮点 0–1 或 mm，可空）：拇指-食指开合度作为与 device 轨 `gripper_width` 同义的连续抓取信号（Dyna-2 伪动作口径；U-23 裁决的"手部状态"显式化）。D2+D1 同戴配对（capture-devices-design §7 ①）用它做伪标签校准。
- **连续帧对导出**：视频流的训练态抽帧不得只保留关键帧；`export` 需支持按 `frame_pair_stride` 输出 (t, t+Δ) 帧对索引，供 WAM 目标（training-pipeline §1.3，U-37）消费。MCAP 采集态不变。
- 其余 0.3 项（逐帧 subtask/plan/progress/reward 列、tactile (N,6)、wrench frame_id、effort measured/estimated、段级表、同意/来源图）见 data-strategy-roadmap §7.2。

## 4. 版本迁移政策

- `schema_version` 采用 `major.minor`；minor 升级只允许**新增可选字段**或**放宽约束**，必须能无损读 0.x 旧数据；major 升级允许删字段，但要提供迁移函数并保留旧 reader 一个里程碑周期。
- 迁移在读侧完成（`fdp.schema.migrate(raw: dict) -> EpisodeMeta`），MCAP 文件本身不回写；ingest 把迁移后的元数据另存到元数据库，raw 永远保留原版本。
- 0.1 → 0.2：`subtask_instructions` 复制到 `subtasks`（区间为 None）；`state` 由 `curated` 推断（True → training_ready，False → ingested）；其余新增字段取 None/空。
- 兼容性测试：`tests/fixtures/episode_v0_1.json` 是冻结的 0.1 样本，每次 schema 改动必须仍能读入（`tests/test_schema.py::test_migrate_v0_1`）。
