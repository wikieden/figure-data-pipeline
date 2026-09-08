# sim 轨落地清单：仿真器 · 资产 · 增殖 · 域随机化 · sim QC · 轨归属

> 2026-09-08。sim 轨在训练配方里承担数据金字塔中层（GR00T 配比合成占 ~98%，research-opensource §6），也是评测 CI 的载体。本文裁决了 governance U-18（动捕/神经轨迹归属）。

## 1. 仿真器选型

| 用途 | 选择 | 理由 |
|---|---|---|
| 主仿真器（增殖 + RL 后训练 + 评测） | **Isaac Lab**（含 Isaac Lab-Arena 批量评测、RLinf VLA 后训练） | GR00T 生态、DexMimicGen 原生、GPU 并行 |
| 轻量基准 | **LIBERO**（MuJoCo）+ **SIMPLEREnv**（real-to-sim） | 社区报数标准（research-vla-pretraining §3.4），单机可跑，CI 用 |
| 备选 | MuJoCo/RoboCasa 直接生成 | 无 GPU 场景；现状未查证（governance R-08 补做项） |

评测 CI 用轻量基准，增殖与 RL 用 Isaac Lab；两者产物都走同一 ingest。

## 2. 资产管线

- 具身资产：与 robot 轨共用 `configs/embodiments/<robot_model>.yaml` + URDF/USD；仿真本体版本哈希进 EpisodeMeta（`robot_model` 含版本后缀）。
- 场景/物体：优先开源资产库（Isaac 内置、Objaverse 子集），自建资产用手机扫描（与 Creator App 的物体标签共用词表 `object_tags`）。
- 每个资产带 license 标注，非商用资产只进研究分支（cleaning-algo-selection 纪律 2 同样适用于资产）。

## 3. 增殖来源与耦合

| 来源 | `source` | 输入 | 输出量级 | 依据 |
|---|---|---|---|---|
| 遥操作回放 | `teleop_replay` | robot 轨 episode 在仿真中重放 | 1:1 | 验证 sim-real 一致性 |
| DexMimicGen 增殖 | `dexmimicgen` | 少量 robot/device 轨演示（10–50 条/任务） | 100–1000× | GR00T：78 万条 ≈ 6,500 h，11 计算小时 |
| 神经轨迹 | `neural_trajectory` | 真机视频微调的视频生成模型（Cosmos/DreamGen 式） | ~10× | GR00T ~827 h |
| 动捕重定向 | `mocap_retarget` | 人体动捕 → 机器人关节空间 | 视动捕量 | Helix S0 路线（本仓库只入湖不训 S0） |
| RL rollout | `rl_rollout` | 仿真 RL 后训练产生 | 海量，默认不入训练集只入评测/奖励 | |

耦合规则：增殖的种子 episode id 写入 `parent_episode_id`；种子若被 curation 标记 `reject_*`，其增殖产物自动降级（lineage 传导）。神经轨迹**必须**经 IDM 打伪动作标签且标 `quality_score`，视同 human 轨伪标签的置信度处理。

## 4. 域随机化版本化

随机化配置（光照、纹理、物体位姿分布、相机抖动、动力学参数）是 yaml 文件 `configs/sim/randomization/<name>.yaml`，哈希进每条 sim episode 的 `/meta/sim` 与 lineage；改配置 = 新版本，不覆盖。评测集所用随机化版本冻结。

## 5. sim 专属 QC

- 物理合理性：穿模检测、接触力异常（>阈值）、关节限位/力矩饱和占比 → `reject_sim_physics`
- 渲染有效性：黑帧/NaN 深度/物体飞出视野
- 增殖成功判定：DexMimicGen 自带的任务成功检查必须为真才入 `training_ready`
- sim-real gap 探针：同任务的 `teleop_replay` 与真机 episode 的轨迹 RMSE 与成功率差，进 eval-protocol §5

## 6. EpisodeMeta 填充与轨归属（裁决 U-18）

- `track = sim`，`source` 必填（§3 表）；`operator_id` 对增殖数据填种子 episode 的操作员（多样性统计沿用）；`scene_id` 填仿真场景 id；`region`/`consent_ref` 为 None。
- **动捕重定向数据归 sim 轨**（`source="mocap_retarget"`）：理由是它与仿真 rollout 一样是"机器人关节空间的合成演示、无真实观测"，训练消费方式相同；不新增 track（决策 2：新增采集形态才新增 track 值，动捕是合成来源不是采集形态）。
- **动捕手套小规模金标准数据**（index-replica-plan §1.0 最后一行）不是训练数据，归 `device` 轨并打 `flag:gold_standard`，只用于伪标签质量分刻度（curation §7）。
- 神经轨迹归 sim 轨（`source="neural_trajectory"`），不归 human 轨：它有（伪）动作标签且观测是生成的。

## 7. 交付

- M1：sim 轨 ingest 适配器（Isaac Lab / LIBERO 录制 → MCAP），`/meta/sim` 消息 schema。
- M2：sim QC 门 + 随机化版本化 + lineage 传导。
- M3：DexMimicGen 增殖流水线接入 mixture-runner；评测 CI（eval-protocol §2）。
