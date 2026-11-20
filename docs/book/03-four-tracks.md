# 第 3 章 四条采集轨与两种采集哲学

## 3.1 四条轨各管什么

| 轨 | 典型来源 | 动作 | 主要价值 | 主要难点 |
|---|---|---|---|---|
| robot | 遥操作、车队自主运行回流 | 真值（关节/末端指令） | 目标本体的精确演示、干预段、成功/失败标签 | 贵、慢；空闲段多；任务模板化，错误容易被批量复制 |
| human | 头戴设备、Creator 手机众包 | 无（需伪标签） | 覆盖面：场景、物体、任务多样性 | 具身鸿沟、无空间锚点、动作短而密、欺诈 |
| device | UMI 手持夹爪、穿戴孪生手套/外骨骼 | 硬件真值（末端位姿、开度、关节） | 对齐层主力：观测与机器人同构、成本低 | 设备入画、抖动、边界难定；只覆盖末端可完成的任务 |
| sim | 仿真增殖、遥操作回放、神经轨迹、动捕重定向、规划轨迹 | 仿真真值或伪动作 | 长尾补充、评测载体、可验证的规划语料 | sim-real gap；生成数据只在专家分布内可信 |

这张表的每一格都有对应的 QC 规则（第 8 章的"四维 × 四轨"矩阵）。分割规则也按轨分开调：device 轨难在设备入画和边界，human 轨难在没有空间锚点，robot 轨难在空闲段多（[curation-pipeline.md](../curation-pipeline.md) §3.2）。

## 3.2 两种采集哲学

四轨背后是两种弥合人→机器人具身鸿沟的对立思路（[architecture.md](../architecture.md) §6.5），本仓库刻意并行两者：

| | 接口对齐（device 轨，UMI / Data Hands） | 表征对齐（human 轨，Index / 头戴视频） |
|---|---|---|
| 思路 | 采集端物理消灭 gap：人与机器人共用同一观测-动作接口（腕装鱼眼 + 同款夹爪 + 末端相对位姿动作） | 数据端全覆盖，靠算法弥合 gap（手部重定向、光流等中间表征） |
| 泛化保证 | 由构造保证：训练与部署分布同构，本体不入观测 | 由模型保证：依赖重定向质量与共训练配方 |
| 代价 | 泛化锚定在"同款末端"；换灵巧手需适配 | 伪标签精度上限、触觉缺失 |
| 任务覆盖 | 末端能完成的任务子集 | 全部日常任务 |
| 规模证据 | Generalist 50 万+ 小时 → GEN-1.5 物理提示涌现 ⚠️ | Index 1,600 万条 + Go-Big 导航零样本迁移（官方） |

**共同点**：接口对齐消灭鸿沟，规模多样性提供燃料，二者缺一不可。device 轨和 human 轨的配比**不由立场决定，由下游消融裁决**——这正是"四轨同 schema、采集方式是组合不是单选"的理论依据。

一个学术旁证：PrimeU（2026-06，论文）显示人类视频零样本迁移依赖人形本体与人类形态的协同设计。Figure 03 的类人形态本身就是 Index 数据能用的前提。

## 3.3 Figure 03 × Index：一对协同设计的采集终端

Figure 的案例值得单独看，因为它展示了 robot 轨和 human 轨如何互为镜像（architecture §1）：

| 维度 | Figure 03（robot 轨，精度腿） | Index（human 轨，规模腿） |
|---|---|---|
| 采集端 | 头部相机 + 双掌心相机 + 指尖触觉 + 全身本体感知 | 手机 App 优先 + 头戴第一视角设备补充 |
| 传输 | 回坞 mmWave 批量卸数（store-and-forward） | 消费级公网上传 |
| 规模引擎 | BotQ 量产 | 众包（108 国、4.4 万周活，官方 ⚠️） |
| 策展 | 精策划（8 小时数据即可出策略） | 五阶段自动化策展管线 |

协同设计的证据链：Figure 03 相机架构官方明说为 Helix 高频视觉运动控制而设计；采集环境就是部署环境（同一物业既供 Index 采数又供机器人部署），刻意最小化域差。

## 3.4 各轨的最小流集合

同 schema 不等于同内容。每条轨有一组"必须有"的流，缺了就拒收或降级（[data-format-contract.md](../data-format-contract.md) §1.3）：

| track | 必须 | 可选 |
|---|---|---|
| robot | ≥1 路 `/video/head*`、`/signal/joint_pos`、`/signal/joint_vel`、`/signal/action`、`/event/intervention`、`/event/task` | 腕部/掌心相机、触觉、末端位姿、底座速度 |
| human | ≥1 路 `/video/ego`、`/imu/head`（有 IMU 时） | SLAM 灰度相机、环境音频、口令事件；众包另带 `/meta/task_goal` |
| device | `/video/ego_wrist`、`/signal/ee_pose`（原生 ≥50 Hz）、`/signal/gripper_width`、`/imu/wrist` | 头戴视角、手套关节 |
| sim | `/video/*`（渲染）、`/signal/joint_pos`、`/signal/action`、`/meta/sim` | 特权信息：物体位姿、接触 |

缺失的可选流在 EpisodeMeta 中不出现即可，训练侧用掩码表达。

## 3.5 sim 轨的六种来源

sim 轨是一个"合成来源"的集合，用 `source` 字段区分（[sim-track.md](../sim-track.md) §3）：

| `source` | 输入 | 输出量级 | 用途 |
|---|---|---|---|
| `teleop_replay` | robot 轨 episode 在仿真中重放 | 1:1 | sim-real 一致性探针 |
| `dexmimicgen` | 每任务 10–50 条种子演示 + 物体/场景表亲 | 100–1000× | 增殖（GR00T：78 万条 ≈ 6,500 h，11 计算小时） |
| `neural_trajectory` | 视频生成模型 | ~10× | 长尾；必须经 IDM 打伪动作并标质量分 |
| `mocap_retarget` | 人体动捕 → 机器人关节空间 | 视动捕量 | S0 全身控制（本仓库只入湖不训） |
| `rl_rollout` | 仿真 RL 后训练 | 海量 | 默认不入训练集，只入评测与奖励 |
| `planning_trace` | SimFoundry 孪生 + BDDL 谓词目标 + 脚本执行器 | 每场景数十任务 × 数百变体 | S2 规划语料与评测，子任务边界和成败为真值；不喂动作专家 |

**耦合规则**：增殖的种子 id 写进 `parent_episode_id`；种子若被策展标记为 `reject_*`，其增殖产物自动降级——lineage 传导。

## 3.6 新的采集任务类型：play 数据

GR00T 2 带来的一个重要启发是：目标本体的数据角色正在从"任务演示"变成"本体说明书"（[gr00t2-trends-analysis.md](../gr00t2-trends-analysis.md) §1.3）。GR00T 2 的 X-Adapt 只用目标本体的 play 数据 + 人 / UMI 演示完成适配；当采集器与执行手一一同构时，连 play 数据都不需要 ⚠️。

本仓库据此新增了 `play.` 前缀的任务模板类型（[robot-track-teleop.md](../robot-track-teleop.md) §5）：按覆盖计划驱动关节空间与工作空间（含双臂相对位姿、手的全行程、各相机视角下的末端外观），不设成功判据。验收看**覆盖度**——关节空间各维分箱填充率、工作空间体素填充率、各相机下末端可见帧占比——不看成功率。play 数据在训练配方里单独成组，不进评测集。

## 3.7 配对采集：对齐层的生产方式

对齐层语料（第 1 章的控制点 2）不是"采更多 robot 数据"，而是**同一任务、同一时刻，用两种采集方式同时录**。[capture-devices-design.md](../capture-devices-design.md) §7 定义了六组配对：

| 配对 | 产出 | 用途 |
|---|---|---|
| 头戴（D2）+ 触觉 UMI（D1）同时佩戴 | 视觉伪标签 vs 硬件真值 | 伪标签质量分定刻度 |
| 头戴 + 固定第三人称相机 | ego + exo 同步对 | 上身对齐动作块 |
| 触觉阵列 + 光学触觉并排 | 跨传感器配对帧 | 触觉迁移 |
| 遥操作手套（D4）+ 本体复现 | 人手关节 vs 机器人关节 | 重定向误差 |
| 手机（D3）vs 头戴（D2）同任务 | 质量差 | 决定哪些众包任务只能用头戴 |
| 头戴脱敏前 vs 后 | 手部可见率、MPJPE 差 | 脱敏损伤基准 |

第一组最关键：它用很低的成本给 human 轨伪标签提供了"标准答案"，比动捕手套方案便宜得多（[device-track-umi.md](../device-track-umi.md) §3）。

## 3.8 本章小结

- 四轨分工：human 管覆盖、device 和 robot 管对齐、sim 管长尾与评测。
- 接口对齐与表征对齐并行，配比由消融裁决而非立场。
- 每条轨有最小流集合；可选流缺失用掩码表达。
- sim 轨是合成来源的集合，`source` 区分，lineage 传导种子质量。
- play 数据是独立的任务类型，验收看覆盖度。
- 对齐层的生产方式是配对采集。

**延伸阅读**：[architecture.md](../architecture.md) §1、§6.5 · [device-track-umi.md](../device-track-umi.md) · [robot-track-teleop.md](../robot-track-teleop.md) · [sim-track.md](../sim-track.md) · [research-four-routes.md](../research-four-routes.md)
