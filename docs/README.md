# 文档索引与阅读路径

> 2026-09-08。本目录是仓库的设计与调研全集；代码只是 M1 骨架，文档是当前真实的"产品"。改任何层之前先读 [architecture.md](architecture.md)；任何设计决策依赖他家数字或有未决项，先登记到 [governance.md](governance.md)。

## 按角色的阅读路径

| 角色 | 顺序 |
|---|---|
| 新成员（30 分钟） | architecture.md（§1、§7、术语表）→ governance.md §2（看哪些还没定）→ 本页文档表 |
| 管理层 / CTO（15 分钟） | data-strategy-roadmap.md §0 与 §6 → §3 对应线条 → program-plan.md |
| 数据层实现者（M1） | architecture §7/§8 → data-format-contract.md → recorder-sync-and-storage.md → ingest-spec.md → device-track-umi.md → CLAUDE.md |
| 策展层实现者（M2） | data-pipeline-design.md → curation-pipeline.md → cleaning-algo-selection.md → governance U-11 license 表 → eval-protocol.md → data-platform.md |
| 训练层（M3） | training-pipeline.md → research-vla-pretraining.md §5 → eval-protocol.md → runtime-and-deployment.md |
| 硬件/采集 | capture-devices-design.md → device-landscape.md → index-replica-plan.md §1 → device-track-umi.md → robot-track-teleop.md → sim-track.md |
| 平台/运维 | data-system-plan.md → data-platform.md → compliance-and-security.md → index-replica-plan.md §2–§3 |
| 项目管理 | data-strategy-roadmap.md §4 → program-plan.md → governance.md → open-source-strategy.md |

## 文档表

### 总设计与治理

| 文档 | 内容 | 成文/最近修订 |
|---|---|---|
| [architecture.md](architecture.md) | 总设计：数据飞轮、管线、训练、验证、RL 闭环、风险、采集哲学、五层框图、里程碑、能力映射表、时间基准与同步 | 2026-08-29 / 2026-09-08 |
| [data-strategy-roadmap.md](data-strategy-roadmap.md) | **战略层**：2026-06..09 十维度态势判断（225 条带来源/可信度）、三条主线与北极星、方向线条 L1–L8、0–24 月实现路径与止损门、五条产品线与商业模式、CTO 拍板清单 | 2026-09-09 |
| [data-pipeline-design.md](data-pipeline-design.md) | **数据管线全链路设计**：对照阿里 Qwen 具身数据链路，入湖 → 质检 → 打标 → 挖掘 → 合成 → 数据集构建 → 回流闭环的总图、环节对照、质检报告与标注档案、挖掘与合成（新增）、lineage 增补、平台自建 vs 阿里云、落地顺序 | 2026-11-17 |
| [data-system-plan.md](data-system-plan.md) | **数据系统规划**：9 个子系统（新增采集任务下发、模型网关与注册、数据服务、人工作业台）、8 类数据产品与 owner、资产目录与状态事件、VLM 与向量索引容量、SLO 增补、运营角色与责任分工、按子系统的建设路线、自建与采购 | 2026-11-17 |
| [gr00t2-trends-analysis.md](gr00t2-trends-analysis.md) | 从 GR00T 2 看后续趋势：数据需求（三层结构、对齐层稀缺、play 数据）、标注引擎化与可重算、硬件（采集器共同设计、头部+双腕、灵巧手与力、三层控制栈）及十项行动清单 | 2026-11-18 |
| [governance.md](governance.md) | 风险登记 R-01–R-19、未决决策 U-01–U-36、自报数字登记 D-01–D-21、回灌清单 | 2026-09-08 / 2026-09-09 |
| [program-plan.md](program-plan.md) | 里程碑验收矩阵（M/H/P 三套前缀）、人力角色、预算总盘 | 2026-09-08 |
| [open-source-strategy.md](open-source-strategy.md) | 开源边界、license 选择、社区与商业分层 | 2026-09-08 |

### 数据层规范（M1）

| 文档 | 内容 | 成文 |
|---|---|---|
| [data-format-contract.md](data-format-contract.md) | MCAP channel/消息 schema、LeRobot v3 映射、EpisodeMeta 字段契约、版本迁移 | 2026-09-08 |
| [recorder-sync-and-storage.md](recorder-sync-and-storage.md) | 机上落盘、flush/fsync、带宽与存储预算、断电恢复 | 2026-09-08 |
| [ingest-spec.md](ingest-spec.md) | 入湖校验、对齐算法、重试/死信、幂等键、断点续传 | 2026-09-08 |
| [capture-devices-design.md](capture-devices-design.md) | 关键采集设备五件套设计：触觉同构 UMI、头戴参考套件、Creator 手机套件、遥操作站 + 手套、车队回流录制器；规格/同步/契约/BOM/验收 | 2026-09-12 |
| [inhouse-isomorphic-end-effector-history-20261026.md](inhouse-isomorphic-end-effector-history-20261026.md) | 历史候选档案：旧三节、驱动假设与迭代概念图，不作为当前规格 | 2026-10-26 |
| [inhouse-isomorphic-end-effector.md](inhouse-isomorphic-end-effector.md) | 当前用户认可的 T/I/S 两节构型：加粗指组、掌面、背侧拇食间向内相机；穿戴采集器、机器人接口、数据契约与验证边界 | 2026-10-26 |
| [device-track-umi.md](device-track-umi.md) | device 轨（UMI 手持夹爪）P0 可执行清单 | 2026-08-29 |
| [robot-track-teleop.md](robot-track-teleop.md) | robot 轨：本体选型框架、遥操作站、接管打点、回流 | 2026-09-08 |
| [sim-track.md](sim-track.md) | sim 轨：仿真器/资产/增殖/域随机化/sim QC/动捕归属 | 2026-09-08 |

### 策展与评测（M2）

| 文档 | 内容 | 成文 |
|---|---|---|
| [curation-pipeline.md](curation-pipeline.md) | 清洗/分割/标注/打包实施规范、episode 状态机、held-out 与泄漏、HITL | 2026-08-29 / 2026-09-08 |
| [cleaning-algo-selection.md](cleaning-algo-selection.md) | 各环节开源算法选型、传统 vs AI 论证、license | 2026-08-29 |
| [eval-protocol.md](eval-protocol.md) | 真机协议模板、指标字典、消融判定规则、仿真基准 | 2026-09-08 |

### 训练与运行时（M3）

| 文档 | 内容 | 成文 |
|---|---|---|
| [training-pipeline.md](training-pipeline.md) | fdp-policy 参考栈、训练课程、工具链、管线升级 | 2026-09-04 / 2026-09-08 |
| [runtime-and-deployment.md](runtime-and-deployment.md) | 部署栈、延迟预算、OOD/reset、回流、安全 | 2026-09-08 |

### 平台与合规

| 文档 | 内容 | 成文 |
|---|---|---|
| [index-replica-plan.md](index-replica-plan.md) | Index 复刻：硬件三阶段、Creator 端、平台、伪标签工厂、训练集成、H0/H1/H2 | 2026-08-29 / 2026-09-08 |
| [dyna-replica-plan.md](dyna-replica-plan.md) | Dyna 模式复现：四层替代、双臂工作站、七项软件缺口、WAM 模型三档、训练数据来源、R0/R1/R2 预算区间与止损门；§12 为当前执行口径（洗衣四任务、仅后训练 + VLM 大脑、自有人形 6 台） | 2026-09-19 / 2026-09-20 |
| [dyna-parity-fast-track.md](dyna-parity-fast-track.md) | 不限资源时追平 Dyna 现状的最快预训练方案：追平判据、数据量重估（30 万小时主力、100 万按曲线裁决）、到货速度、F0–F4 时间线、算力 / 农场 / 团队、12 个月预算、钱买不到的约束 | 2026-09-20 |
| [laundry-sorting-brain-plan.md](laundry-sorting-brain-plan.md) | 脏衣服分类的识别与决策大脑训练计划：三层结构（视觉前端 / VLM 属性与洗标 / 规则分筐）、属性本体、数据与标注、S0–S9 训练阶段、校准与弃权、指标与验收、日志回流格式 | 2026-09-20 |
| [plans-review-hard-points.md](plans-review-hard-points.md) | 方案评审：洗衣两套方案、分类大脑、叠晾计划、追平 Dyna 最快路线、D1-H 的难点与卡点排序、逐项对策、前 4 周去风险清单、需领导新增拍板的事项 | 2026-09-20 |
| [laundry-fold-hang-plan.md](laundry-fold-hang-plan.md) | 交付二（叠 / 晾 / 收纳）：大脑 v2 与共用动作原语的分工、规范化、结构类数据覆盖、跨品类泛化探针（兼方案 B 启动判据）、品类白名单 | 2026-09-20 |
| [laundry-two-plans-brief.md](laundry-two-plans-brief.md) | 管理层汇报稿：洗衣房四任务的后训练方案 vs 预训练方案，效果、成本、训练流程、数据与管线需求、风险与决策请求 | 2026-09-20 |
| [hisense-capture-to-training-report.md](hisense-capture-to-training-report.md) | 研究报告：各家采集设备与方案横评（动作真值 / 观测同构 / 力 / 规模 / 换代存活度对训练算法的影响），海信家务与无人洗衣房的五件采集设备（含家电事件流）、管线增量、三层模型与四阶段课程、长期通用能力护栏 | 2026-11-06 |
| [data-platform.md](data-platform.md) | 容量/成本模型、组件选型、lineage 表结构、可观测性 | 2026-09-08 |
| [compliance-and-security.md](compliance-and-security.md) | 区域矩阵、Creator 协议、保留期、RBAC/审计、安全基线、劳动合规 | 2026-09-08 |

### 调研（只读依据，引用时看可信度标注）

| 文档 | 内容 | 成文 |
|---|---|---|
| [research-figure.md](research-figure.md) | Figure Helix/Figure 03/Index 已核查事实（官方 vs 第三方） | 2026-08-29 |
| [research-opensource.md](research-opensource.md) | 开源生态选型（MCAP/LeRobot/rerun/AV1/仿真） | 2026-08-29 |
| [research-generalist-dora.md](research-generalist-dora.md) | Generalist GEN 系、Data Hands、dora-rs | 2026-08-29 |
| [research-vla-pretraining.md](research-vla-pretraining.md) | 清洗→VLA/WAM 0→1 预训练全链路，含可行计划 | 2026-08-30 |
| [research-qwen-robotics.md](research-qwen-robotics.md) | 通义机器人栈 + 阿里云具身数据管线方案（现场 slide + 客户交流 PDF，非公开） | 2026-11-02 |
| [research-sunday.md](research-sunday.md) | Sunday Memo / Skill Capture Glove | 2026-09-04 |
| [research-sensor-layouts.md](research-sensor-layouts.md) | 已调研产品机器人本体的传感器设计对照（Figure 03 / Dyna / Sunday Memo / Generalist 机器人端），每台一张布局示意图，位置可信度分级 | 2026-09-16 |
| [research-end-effector-torso.md](research-end-effector-torso.md) | 四家末端机构与腰部/躯干机构对比（谁服从谁：采集端同构 vs 真值维度），直接服务 U-04 与本体选型 | 2026-09-16 |
| [research-model-recipes.md](research-model-recipes.md) | 五家模型实现对比（Helix VLA / DYNA-2 WAM / ACT / GEN / Skild Brain）：架构、训练流程、目标函数、推理回路、五个分歧轴 | 2026-09-16 |
| [research-twindex.md](research-twindex.md) | 自变量 TwinDEX 孪生灵巧手 | 2026-09-04 |
| [research-xsquare.md](research-xsquare.md) | 自变量数据管线全景（13 份一手归档）：真机遥操 + XRZero-G0/QUANXTA Zero 无本体采集 + TwinDEX + X2Real 仿真合成；同步、清洗质检（含真机物理回放门）、两级指令与具身桥接样本、无本体:真机 1:1/10:1 配比律、幂采样；自报数字可信度与行动项 | 2026-11-02 |
| [device-landscape.md](device-landscape.md) | 领先采集设备构型横评（多角度图集） | 2026-09-04 |
| [research-simfoundry.md](research-simfoundry.md) | NVIDIA SimFoundry：单视频→仿真孪生/数字表亲，real2sim 评测与 sim2real 训练，license 边界 | 2026-09-09 |
| [research-gr00t2.md](research-gr00t2.md) | NVIDIA GR00T 2 世界-动作模型：架构与推理、三阶段训练、人类视频/UMI/遥操配比，以及数据管线（人类 QC 窗口阈值、in-lab 采集验收、UMI 三级质检、Flora 标注、Lance 快照与 QC 视图、处理管线、GearArena 盲测 A/B）与本仓库对照 | 2026-11-18 |
| [research-dyna-comparison.md](research-dyna-comparison.md) | Dyna DYNA-1/DYNA-2 模型与数据方案；与 Generalist GEN-0/1/1.5、Skild S1、已研究厂商及学术四个接口的横向对比 | 2026-09-14 |
| [research-four-routes.md](research-four-routes.md) | Figure / Dyna / Sunday / Generalist 四家技术路线精读（37 篇一手页面）：本体·数据·模型·部署评测四层对照，分歧与收敛点，回写清单 | 2026-09-14 |
| [research-skild.md](research-skild.md) | Skild AI 一手调研（11 篇博客）：Skild Brain 分层、全身体仿真、S1 视频提示 ICL 与 1k–100k h scaling、L1–L5 扰动阶梯、$1:$3 质控、部署飞轮观 | 2026-09-14 |
| [research-open-ecosystem-2026.md](research-open-ecosystem-2026.md) | 开源生态全景：开放数据集（真机/人类视频/手持设备/仿真，含 license 与口径冲突）、仿真与真机基准（含 2026-06 基准审计结论）、开放权重模型骨架矩阵（VLA 四谱系 + WAM）、训练框架对比、预训练/微调/推理/存储资源账 | 2026-10-13 |
| [research-rd-tooling.md](research-rd-tooling.md) | 研发工具链：中间件（ROS 2/Zenoh/rosbag2 MCAP/dora-rs/Copper-rs）、仿真与物理引擎（MuJoCo Warp/Newton/Isaac Lab 3.0/Genesis/ManiSkill3）、资产转换、人形全身控制与重定向（SONIC/mjlab/GMR）、规划与动力学（cuRoboV2/Pinocchio/Crocoddyl/Drake）、部署推理、数据平台、建图定位（cuVSLAM/nvblox/RTAB-Map/GLIM/MapAnything/VGGT）、导航（Nav2/InternNav/场景图）、多模态感知（Depth Anything 3/MoGe/CoTracker）、分割识别（SAM 2/3、Grounded-SAM-2、RF-DETR/D-FINE，AGPL 与非商用项标出）；license 按 LICENSE 原文核对；LeRobot 0.7 破坏性改动与回写清单 | 2026-11-05 |
| [research-commercial-deployments.md](research-commercial-deployments.md) | 已调研厂商的商用落地案例：酒店洗衣房、餐厅厨房（Dyna 鼎泰丰/Monster Laundry、Skild 三井物产厨房试点）及工厂/物流/家庭，按规模部署/试点/演示分档 | 2026-10-09 |
| [sources/MANIFEST.md](sources/MANIFEST.md) | 一手资料归档：Figure 18 / Dyna 8 / Sunday 4 / Generalist 10 / Skild 11 / 自变量 13 篇官网原文文本（URL、页面日期、抓取日期、HTML sha256），research 文档的引用目标 | 2026-09-14 |

`reports/` 存管理层汇报页的单文件 HTML（[洗衣房两套方案](reports/laundry-two-plans.html)、[追平 Dyna 最快路线](reports/dyna-parity-fast-track.html)、[业内七条路线对照与取舍](reports/industry-routes.html)），前两份分别对应 laundry-two-plans-brief.md 与 dyna-parity-fast-track.md，第三份汇总 research-*.md 与 data-strategy-roadmap.md §1 的已核查条目，更新汇报页时同步覆盖。

`assets/` 存文档图片（16 张，均在对应文档标注来源）。

## 三套里程碑前缀

- **M1/M2/M3**：工程里程碑，按管线层（architecture §7）
- **H0/H1/H2**：Index 复刻硬件/平台时间线（index-replica-plan §7）
- **P0/P1/P2**：采集硬件成熟度（index-replica-plan §1）
- 对外产品线用 **PL1–PL5**（data-strategy-roadmap §5），不与 P0/P1/P2 混用
