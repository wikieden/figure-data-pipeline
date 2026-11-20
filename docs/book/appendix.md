# 附录

## A. 术语表

| 术语 | 定义 | 首次出现 |
|---|---|---|
| track（轨） | 采集形态的枚举：robot / human / device / sim；同一 EpisodeMeta，`track` 字段区分 | 第 2、3 章 |
| source | sim 轨的子来源（`teleop_replay`、`dexmimicgen`、`neural_trajectory`、`mocap_retarget`、`rl_rollout`、`planning_trace`、提议中的 `human2robot_composite`），或 robot 轨回流的 `fleet` | 第 3 章 |
| session（会话） | 一名采集者一次连续佩戴或开机到关机的过程，含多个 episode | 第 9 章 |
| episode | 一次任务尝试的完整记录，策展与训练的基本单位 | 第 6 章 |
| segment（子任务段） | episode 内按子任务边界切出的区间，带子任务级指令 | 第 9 章 |
| clip（切片） | 从 segment 裁出的 3–12 s 干净片段，进演示库 | 第 9 章 |
| 演示库 | 按任务 embedding 可检索的切片集合，训练分片之外的第二产物 | 第 11 章 |
| 入湖（ingest） | 原始文件进入数据湖：校验、对齐、转码、登记 | 第 7 章 |
| 质量门 | 策展中的自动过滤阶段，含 L1 运动学 / L2 统计 / L3 VLM 语义 | 第 8 章 |
| 规则段 / 语义段 / 报告段 | 质检的三段执行：确定性检查 / VLM 先粗后细 / 合并出报告 | 第 8 章 |
| 样本窗口判定 | 按训练样本实际读取的时间窗判定合格与否，而不是整段 episode | 第 8 章 |
| QC 视图 | 判定结果作为列追加，export 时离线生成合格样本起点视图 | 第 12 章 |
| 两把尺子 | 分割验收的宽松（切点 F1）与严格（IoU ≥0.75 一对一）两种口径 | 第 9 章 |
| 槽位化描述 | 按动作、对象、目标位置、结果状态等槽位结构化存储的子任务描述 | 第 9 章 |
| 标注档案 | 按用途（`action_expert` / `planner` / `pretrain`）组装的标注规格 | 第 9 章 |
| 待裁决队列 | 标注规范未覆盖情况的裁决队列，裁决结果回写规范并版本化 | 第 9 章 |
| 伪标签工厂 | human 轨从视频恢复动作标签的处理链 | 第 10 章 |
| 具身转换 | 把穿戴/头戴 device 子形态 episode 变换为机器人域 episode 的可选阶段 | 第 10 章 |
| 再平衡 | 按任务 × 物体 × 环境 × 操作者聚类调整采样权重 | 第 11 章 |
| 挖掘 | 结构化过滤 + embedding 召回 + 精排的检索环节 | 第 11 章 |
| 查询快照 | 一次挖掘查询的结果清单与分数，写入 lineage，可被 manifest 引用 | 第 11 章 |
| 槽位向量 | 96 维固定布局的状态/动作表示 + 有效掩码 | 第 12 章 |
| manifest | 冻结的数据集清单：episode 与哈希、配方、查询快照、标注版本、切分版本、QC 视图 | 第 12 章 |
| held-out | 入湖后、策展前固定的评测切分，按场景与操作者组切分，永不回流 | 第 12 章 |
| 配方（mixture） | `configs/mixtures/*.yaml`，各轨/任务簇/质量层的采样权重与温度 | 第 13 章 |
| play 数据 | 与任务无关、只交代本体怎么动与长什么样的数据，按覆盖度验收 | 第 3 章 |
| 配对采集 | 同一任务同一时刻用两种方式同时采集，产出对齐层语料 | 第 3 章 |
| 干预段 | 部署或遥操作中人工接管前后的片段，最贵的对齐层数据 | 第 14 章 |
| loop 记录 | 每轮回流闭环的完整记录，飞轮是否在转的唯一证据 | 第 14 章 |
| lineage | 从训练分片到策展决策到原始上传的全链路记录 | 第 15 章 |
| 北极星 | 新任务上线成本：新任务真机达标所需的真机小时与全成本 | 第 1 章 |

## B. 关键数字与可信度

书中用到的他家数字，按来源属性归类。⚠️ 为公司自报，仅用于判断方向或给阈值定起点，不作为设计参数。登记号见 [governance.md](../governance.md) D 表。

| 数字 | 来源属性 | 本书用途 | 章 |
|---|---|---|---|
| Figure 用 8 小时精策划数据即出可用策略 | 官方 | 质量优先于吞吐的依据 | 2 |
| Index 每 1,000 小时 373 任务 / 1,146 物体 / 116 环境 | 自报 ⚠️（分母口径未公开，D-09） | 多样性 KPI 对照，不直接比较 | 11 |
| Index 五阶段策展丢弃大部分原始上传 | 第三方（Forbes） | 可用远小于名义 | 1 |
| GR00T 2 预训练混合：人类视频 ~92%、遥操 ~5%、UMI ~2% | 一手架构自述，比例自报 ⚠️（D-34） | 三层数据结构 | 1 |
| GR00T 2 UMI 三级质检滤掉约 1/4（站侧 ~11%、agent ~16%） | 自报 ⚠️ | device 轨三级执行 | 8 |
| GR00T 2 human 窗口阈值（头角速度 ≤20°/s 等） | 自报 ⚠️ | v0 临时阈值 | 8 |
| GR00T 2 Flora 两天重标约 40 万小时 | 自报 ⚠️ | 标注引擎化趋势 | 9 |
| GR00T 2 仿真-真机 Pearson 0.92–0.93 | 自报 ⚠️ | 仿真替代真机的条件 | 14 |
| 某大模型厂商 Ego 质检阈值（Laplacian <100 等） | 自报 ⚠️（D-33） | v0 临时阈值 | 8 |
| 某大模型厂商两把尺子：宽松差 2.7×、严格差 7.5× | 自报 ⚠️（D-33） | 为什么要同时报两把尺子 | 9 |
| 某大模型厂商粒度与用途不匹配训练效果下降 60% | 自报 ⚠️（D-33） | 标注档案 | 9 |
| 厂商论文 1,933 h 人类视频 → 15 种本体 24,808 h（≈12.8×） | 论文（D-11 口径） | 人→机合成 | 10 |
| SimFoundry real2sim Pearson 0.911 / MMRV 0.018 | 论文 | 仿真保真度门槛参照 | 14 |
| DexMimicGen：78 万条 ≈ 6,500 h，11 计算小时 | 论文（GR00T） | 仿真增殖量级 | 3、10 |
| Dyna MCAP + topic 分组：存储 −68%、读延迟 2.9× | 自报 ⚠️ | 按读取模式分组 topic | 6 |
| Octo 93M ≈ RT-2 55B；OpenVLA 7B > RT-2-X 55B | 论文 | 规模换参数 | 13 |
| HIL-SERL 真机 1–2 小时近满成功率 | 论文 | RL 闭环 | 13 |
| 潜动作 0.14 vs 光流中间表征 0.69（MetaWorld） | 论文 | 显式中间表征更可靠 | 10 |
| 众包第一视角视频 ~$6/小时 | 第三方 | 供给过剩 | 1 |
| 平台成本约 $6–8 / 可用小时（H1） | 本仓库估算 | 单位经济 | 15 |

## C. 章节与规范文档对照

书中内容以下列规范为准，冲突时以规范为准并登记到 governance。

| 章 | 主要规范文档 |
|---|---|
| 1 瓶颈 | [data-strategy-roadmap.md](../data-strategy-roadmap.md) §0–§2、[gr00t2-trends-analysis.md](../gr00t2-trends-analysis.md) |
| 2 决策 | [CLAUDE.md](../../CLAUDE.md)、[architecture.md](../architecture.md) §7 |
| 3 四轨 | [architecture.md](../architecture.md) §1/§6.5、[device-track-umi.md](../device-track-umi.md)、[robot-track-teleop.md](../robot-track-teleop.md)、[sim-track.md](../sim-track.md) |
| 4 设备 | [capture-devices-design.md](../capture-devices-design.md)、[recorder-sync-and-storage.md](../recorder-sync-and-storage.md)、[inhouse-isomorphic-end-effector.md](../inhouse-isomorphic-end-effector.md) |
| 5 时间同步 | [architecture.md](../architecture.md) §8 |
| 6 契约 | [data-format-contract.md](../data-format-contract.md) |
| 7 入湖 | [ingest-spec.md](../ingest-spec.md)、[data-pipeline-design.md](../data-pipeline-design.md) §3 |
| 8 质检 | [curation-pipeline.md](../curation-pipeline.md) §0–§1、[cleaning-algo-selection.md](../cleaning-algo-selection.md)、[data-pipeline-design.md](../data-pipeline-design.md) §4 |
| 9 分割标注 | [curation-pipeline.md](../curation-pipeline.md) §3–§4/§7/§9、[data-pipeline-design.md](../data-pipeline-design.md) §5 |
| 10 伪标签合成 | [curation-pipeline.md](../curation-pipeline.md) §4.2、[data-pipeline-design.md](../data-pipeline-design.md) §7、[sim-track.md](../sim-track.md) |
| 11 去重挖掘 | [curation-pipeline.md](../curation-pipeline.md) §2、[data-pipeline-design.md](../data-pipeline-design.md) §6 |
| 12 数据集 | [data-format-contract.md](../data-format-contract.md) §2、[curation-pipeline.md](../curation-pipeline.md) §5/§8 |
| 13 训练消费 | [training-pipeline.md](../training-pipeline.md)、[research-vla-pretraining.md](../research-vla-pretraining.md) |
| 14 评测闭环 | [eval-protocol.md](../eval-protocol.md)、[data-pipeline-design.md](../data-pipeline-design.md) §9、[runtime-and-deployment.md](../runtime-and-deployment.md) |
| 15 平台系统 | [data-system-plan.md](../data-system-plan.md)、[data-platform.md](../data-platform.md) |
| 16 合规治理 | [compliance-and-security.md](../compliance-and-security.md)、[governance.md](../governance.md) |
| 17 路线 | [data-strategy-roadmap.md](../data-strategy-roadmap.md) §4–§5、[program-plan.md](../program-plan.md) |

## D. 修订记录

| 日期 | 内容 |
|---|---|
| 2026-11-20 | 初版：基于截至 2026-11-18 的仓库文档整理，17 章 + 附录 |
