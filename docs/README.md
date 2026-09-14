# 文档索引与阅读路径

> 2026-09-08。本目录是仓库的设计与调研全集；代码只是 M1 骨架，文档是当前真实的"产品"。改任何层之前先读 [architecture.md](architecture.md)；任何设计决策依赖他家数字或有未决项，先登记到 [governance.md](governance.md)。

## 按角色的阅读路径

| 角色 | 顺序 |
|---|---|
| 新成员（30 分钟） | architecture.md（§1、§7、术语表）→ governance.md §2（看哪些还没定）→ 本页文档表 |
| 管理层 / CTO（15 分钟） | data-strategy-roadmap.md §0 与 §6 → §3 对应线条 → program-plan.md |
| 数据层实现者（M1） | architecture §7/§8 → data-format-contract.md → recorder-sync-and-storage.md → ingest-spec.md → device-track-umi.md → CLAUDE.md |
| 策展层实现者（M2） | curation-pipeline.md → cleaning-algo-selection.md → governance U-11 license 表 → eval-protocol.md → data-platform.md |
| 训练层（M3） | training-pipeline.md → research-vla-pretraining.md §5 → eval-protocol.md → runtime-and-deployment.md |
| 硬件/采集 | capture-devices-design.md → device-landscape.md → index-replica-plan.md §1 → device-track-umi.md → robot-track-teleop.md → sim-track.md |
| 平台/运维 | data-platform.md → compliance-and-security.md → index-replica-plan.md §2–§3 |
| 项目管理 | data-strategy-roadmap.md §4 → program-plan.md → governance.md → open-source-strategy.md |

## 文档表

### 总设计与治理

| 文档 | 内容 | 成文/最近修订 |
|---|---|---|
| [architecture.md](architecture.md) | 总设计：数据飞轮、管线、训练、验证、RL 闭环、风险、采集哲学、五层框图、里程碑、能力映射表、时间基准与同步 | 2026-08-29 / 2026-09-08 |
| [data-strategy-roadmap.md](data-strategy-roadmap.md) | **战略层**：2026-06..09 十维度态势判断（225 条带来源/可信度）、三条主线与北极星、方向线条 L1–L8、0–24 月实现路径与止损门、五条产品线与商业模式、CTO 拍板清单 | 2026-09-09 |
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
| [data-platform.md](data-platform.md) | 容量/成本模型、组件选型、lineage 表结构、可观测性 | 2026-09-08 |
| [compliance-and-security.md](compliance-and-security.md) | 区域矩阵、Creator 协议、保留期、RBAC/审计、安全基线、劳动合规 | 2026-09-08 |

### 调研（只读依据，引用时看可信度标注）

| 文档 | 内容 | 成文 |
|---|---|---|
| [research-figure.md](research-figure.md) | Figure Helix/Figure 03/Index 已核查事实（官方 vs 第三方） | 2026-08-29 |
| [research-opensource.md](research-opensource.md) | 开源生态选型（MCAP/LeRobot/rerun/AV1/仿真） | 2026-08-29 |
| [research-generalist-dora.md](research-generalist-dora.md) | Generalist GEN 系、Data Hands、dora-rs | 2026-08-29 |
| [research-vla-pretraining.md](research-vla-pretraining.md) | 清洗→VLA/WAM 0→1 预训练全链路，含可行计划 | 2026-08-30 |
| [research-qwen-robotics.md](research-qwen-robotics.md) | 通义机器人栈（现场 slide，非公开） | 2026-09-04 |
| [research-sunday.md](research-sunday.md) | Sunday Memo / Skill Capture Glove | 2026-09-04 |
| [research-twindex.md](research-twindex.md) | 自变量 TwinDEX 孪生灵巧手 | 2026-09-04 |
| [device-landscape.md](device-landscape.md) | 领先采集设备构型横评（多角度图集） | 2026-09-04 |
| [research-simfoundry.md](research-simfoundry.md) | NVIDIA SimFoundry：单视频→仿真孪生/数字表亲，real2sim 评测与 sim2real 训练，license 边界 | 2026-09-09 |
| [research-dyna-comparison.md](research-dyna-comparison.md) | Dyna DYNA-1/DYNA-2 模型与数据方案；与 Generalist GEN-0/1/1.5、Skild S1、已研究厂商及学术四个接口的横向对比 | 2026-09-14 |
| [research-four-routes.md](research-four-routes.md) | Figure / Dyna / Sunday / Generalist 四家技术路线精读（37 篇一手页面）：本体·数据·模型·部署评测四层对照，分歧与收敛点，回写清单 | 2026-09-14 |

`assets/` 存文档图片（16 张，均在对应文档标注来源）。

## 三套里程碑前缀

- **M1/M2/M3**：工程里程碑，按管线层（architecture §7）
- **H0/H1/H2**：Index 复刻硬件/平台时间线（index-replica-plan §7）
- **P0/P1/P2**：采集硬件成熟度（index-replica-plan §1）
- 对外产品线用 **PL1–PL5**（data-strategy-roadmap §5），不与 P0/P1/P2 混用
