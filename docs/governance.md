# 治理登记：风险 · 未决决策 · 自报数字

> 2026-09-08 建立，2026-09-09 增补（战略路线图引出的 U-23–U-33 / R-14–R-19 / D-13–D-21；2026-09-14 增补 U-37 / R-20 / D-22–D-24，U-11 表 23–30 行；2026-09-19 增补 U-39 / R-21，U-11 表 31–32 行；2026-09-20 增补 U-40；同日方案评审增补 R-22–R-25、U-41、U-42）；同日逐项裁决 data-strategy-roadmap §6 的 10 项决策（U-03/U-23/U-24/U-25/U-27/U-28/U-30/U-32 closed，U-26 部分裁决，U-29 拆表后逐项待 LEGAL）；同日追加裁决 U-09/U-22/U-31/U-33；2026-09-12 增 U-34–U-36（采集设备五件套）；2026-09-14 增 U-38 / D-25–D-27（四家路线精读 research-four-routes.md），同日 D-23 由第三方改一手（research-skild.md）。来源为全局 review 三路审计（一致性 / 覆盖缺口 / 风险与未决项）的合并结果。三张表是活文档：每条有 owner（按角色，非人名）与复检时点；状态字段只有 `open / mitigating / closed / accepted`。新增风险、新增依赖他家数字的设计决策、新增待裁决项都必须先在这里登记再写进设计文档（CLAUDE.md 约定）。

角色缩写：**DATA** 数据层（recorder/ingest/export/schema）、**CUR** 策展层、**TRAIN** 训练层、**HW** 采集硬件、**PLAT** 数据平台/运维、**LEGAL** 法务合规、**PM** 项目管理。

---

## 1. 风险登记（R）

| ID | 类别 | 风险 | 严重度 | 触发条件 / 观测信号 | 对策 | owner | 复检 | 状态 |
|---|---|---|---|---|---|---|---|---|
| R-01 | 合规 | 隐私合规：进家庭众包采集；"raw 永存"与存储限制原则冲突；误模糊不可逆 | 高 | 任一区域上线前；误模糊率 >0.1% | [compliance-and-security.md](compliance-and-security.md)：保留期政策、DPIA 触发条件、删除 SLA、误模糊率进 QC、脱敏前哈希留存 | LEGAL | H0 末、每季度 | mitigating |
| R-02 | 经济 | 单位经济不成立：每可用训练小时全成本长期高于遥操作 | 高 | 连续两季度 > 遥操作 1/2 且不降 | 止损阈值写入 index-replica-plan §8.4；容量/成本模型 [data-platform.md](data-platform.md) §1；存储成本纳入 | PM | 每季度 | open |
| R-03 | 诚实性 | 采信他家自报数字而无对冲；对外宣称不可复现 | 中 | 设计决策引用未登记数字 | 本文 §3 D 表 + CLAUDE.md 钩子；对外宣称附可复现日志与干预率（[eval-protocol.md](eval-protocol.md)） | PM | 每次新增 research 文档 | mitigating |
| R-04 | 数据 | human 轨无触觉/力学，接触密集任务天花板未知 | 中 | fewshot-bench 在接触密集任务簇上 human 轨增量 ≈0 | **2026-09-09 更新**：human 轨定位由"规模腿"改为预训练主轴、robot/device 轨为对齐层（[data-strategy-roadmap.md](data-strategy-roadmap.md) §1.1，architecture §1 表待回写）；对策改为触觉 UMI 500 h 对照集（U-25）+ 按任务簇拆分的 human 轨增量消融（eval-protocol §3，止损门 G2）；P2 EMG/音频探针并入 U-09 | TRAIN | Stage B 起每数据版本 | mitigating |
| R-05 | 平台 | 众包欺诈；漏检率无 ground truth | 中 | 欺诈率 >1% 或漏检率不可测 | 红队植入测试集（每月投放已知欺诈样本测漏检率，[data-platform.md](data-platform.md) §5）；计酬锚定通过分钟 | PLAT | 每月 | mitigating |
| R-06 | 数据 | 伪标签质量上限；六因子质量分公式未验证 | 高 | 金标准配对集 Spearman <0.5；H0 "伪标签→仿真收益"不见收益 | curation-pipeline §7 增加公式验收；H0 止损门；金标准来源与规模在 [sim-track.md](sim-track.md) §6 动捕条目 | CUR | H0 末 | open |
| R-07 | 硬件 | 设备标定漂移与 GoPro 时戳抖动导致大批拒收 | 中 | `flag:calib_stale` 或 `reject_timing` 占比 >5% | architecture §8.5 在线再估计 + 待重标队列；ingest 先实测 GoPro 抖动分布再定阈值（[ingest-spec.md](ingest-spec.md) §2） | DATA | M1 ingest 实现时 | open |
| R-08 | 流程 | 调研证据链不完整：research-opensource 由挂起 agent 的 13 组结果综合；architecture 对抗核查未完成；Generalist/TwinDEX 官网抓取受限 | 中 | 选型依赖单一来源 | 补做清单：lerobot-dataset API 面核查（M1 export 前）、MuJoCo 侧仿真现状（sim-track）、Foxglove 转型影响评估；单来源论断保持 ⚠️ 标注 | PM | M1 末 | open |
| R-09 | 依赖 | 商业 VLM API 在数据生产关键路径：可用性、版本漂移无权重哈希、输出用于训练数据的条款未审 | 中 | API 不可用 >1h；API 版本变更 | 本地 Qwen-VL 主力，API 只做分歧仲裁且可降级；lineage 记模型名+API 版本+日期（cleaning-algo-selection 纪律 4）；ToS 进 license 终审 | CUR + LEGAL | H0 末 | mitigating |
| R-10 | 依赖 | 上游生态单点：LeRobotDataset v3 唯一训练格式；MCAP/Foxglove/Rerun 生态方向变化 | 中 | **2026-09-09 重开**：`lerobot-dataset` 独立包停在 0.5.0 无更新；LeRobot 0.7 路线图"流优先"重设计；Rerun 发布 .rrd 数据层 + Hub 成为第三种持久化格式候选 | 训练态依赖改为 `lerobot` 核心包（≥0.6）并锁版本；export 层 writer 接口保留以承接 0.7 流优先；Rerun .rrd 只作可视化缓存不作持久化（决策 1 不变）；MCAP 规范开放可自维护 reader | DATA | 每季度 | open |
| R-11 | 合规/安全 | 人口与地域偏差；按分钟计酬的用工性质；上门服务人身安全；上传内容安全 | 中 | 再平衡簇覆盖按地域/人群严重不均；任一区域劳动法咨询意见为"雇佣" | 再平衡加操作者轴（curation §2.2）；劳动合规、背景审查、内容安全流程在 [compliance-and-security.md](compliance-and-security.md) §7–§9 | LEGAL + PLAT | H1 前 | open |
| R-12 | 流程 | 文档同步失效：research 新发现不回灌总设计（Ego2Robot 三套数字、具身转换未进架构、embedding 选型两文档相反、GPL 未传导） | 中 | 同一事实两处不一致 | docs/README.md 索引 + "research → 设计"回灌清单（§4）；每份 research 文档末尾必须有"已同步到"行；CI 链接扫描 | PM | 每次 review | mitigating |
| R-13 | 流程 | 设计-实现漂移无追踪 | 低 | 设计写明"已落地"但代码无 | training-pipeline §4 状态列；architecture §7 能力→模块表；测试基线（schema 兼容、CLI smoke、golden fixture） | DATA | 每里程碑 | mitigating |
| R-14 | 数据 | 采集速度多模态污染：以操作者数量为再平衡目标会引入速度分布多峰，损害策略（GO-1-Pro v2）；Sunday 要求采集员刻意放慢 | 中 | 同任务速度带方差 >2× 且策略在快慢样本上成功率差 >10pt | 采集 SOP 定义速度带并记入 EpisodeMeta，速度带作为独立元数据轴；操作者轴保留用于人口/地域覆盖（R-11）与 held-out 组切分，但不作为策略性能的再平衡目标；ISR 重采样作 export 选项（[data-strategy-roadmap.md](data-strategy-roadmap.md) L1/L3） | CUR | M2 | open |
| R-15 | 依赖 | LeRobot 0.7 流优先重设计的破坏性变更（episode 变派生视图） | 中 | 0.7 正式版破坏 v3 读侧或 `fdp.*` 扩展列 | 冻结在 0.6 一个季度评估；writer 接口抽象；必要时自维护 v3 reader | DATA | 0.7 发布时 | open |
| R-16 | 数据 | 估值分数（影响函数/medoid/PSD）过拟合当前策略与当前任务簇 | 中 | 估值 top-50% 训练不优于随机 50%（止损门 G5） | 估值只作排序不作删除；每季度用新策略重算；held-out 上不做任何估值决策 | CUR | M3 | open |
| R-17 | 评测 | 世界模型代理评测在 off-expert 动作区失效（WorldSimProbe/WorldEcho），误判策略排序 | 高 | 代理与真机 Pearson <0.8 连续两季度（止损门 G4） | 代理必须附"可观测模拟器契约"测试；只在专家动作分布内使用；三层（孪生→代理→真机）相关性每季度重估 | TRAIN | M3 起每季度 | open |
| R-18 | 数据/合规 | 端上脱敏损伤手部可见率与动作伪标签（脱敏是 raw 永存唯一例外，且因旁观者诉讼必须前置） | 中 | 脱敏后 MPJPE 差 >10% 或手部可见率降 >5pt | 脱敏工具链选型消融（U-32）；脱敏前帧哈希留存 90 天；损伤指标进 QC | CUR + LEGAL | H0 末 | open |
| R-19 | 商业 | 对外策展/评测服务的客户即竞争者（训练场自建策展）；开源工具与商业服务自我冲突 | 低 | 客户流失到自建；开源阈值被要求公开 | **2026-09-09 裁决**：PL3 策展即服务为对外首条产品线（M2 后，12 个月内 2 家训练场）；契约与报告器免费、估值与评测校准数据收费；方法公开、阈值与配方版本化不公开（open-source-strategy §5） | PM | 对外首单前 | mitigating |
| R-20 | 商业/闭环 | 部署车队不产生自加速飞轮：Dyna 联创 York Yang（2026-05）自述 10 个月、多客户、每天 16 h 运营"部署没有自我加速"，并称全行业同此（research-dyna-comparison §2.4） | 高 | L7 回流小时数增长但"干预段 → 下一版本成功率增量"转化率不升；PL5 收入假设失据 | **2026-09-14 新增**。对策：闭环层 KPI 改为转化率而非回流小时；D5 只固化干预/OOD 段；G5 门加转化率阈值；PL5 商业假设按 Dyna 反证打折 | 数据负责人 | G5 |
| R-21 | 训练/预算 | Dyna 复现方案的关键参数全为我方估算：Dyna 未披露骨干来源、参数量、训练算力、λ、分辨率、动作分支深度（[dyna-replica-plan.md](dyna-replica-plan.md) §4）；预算区间可能偏差一个档位 | 中 | R0 调试算力超出 30% 余量；单卡推理达不到 10 Hz；三种配方对照结论随超参翻转 | **2026-09-19 新增**。对策：未披露项一律当超参扫；G-R0a（第 3 月）专设推理延迟门；只批 R0，R1 以 G-R0b 为条件；预算每档独立止损 | 训练负责人 | G-R0a / G-R0b |
| R-22 | 硬件 | 自研轮式人形 6 台的可用率未知：加速版假设 4 台并行采集 + 1–2 台评测，无 MTBF 数据（[plans-review-hard-points.md](plans-review-hard-points.md) X-1） | 高 | 周可用率 <60%；同一故障重复出现 | **2026-09-20 新增**。逐台可用率台账；备件包；专人本体工程师；1–2 台固定上半身台架做采集缓冲；低于 60% 按比例顺延并上报 | HW + PM | 每周 | open |
| R-23 | 依赖 | 洗烘机器无法由程序启动：家用机远程启动常需每次在面板手动开启 ⚠️ 未核查，商用机多无开放接口 ⚠️（W-1） | 中 | 选定机型接口验证失败 | **2026-09-20 新增**。接口与"机器人按面板（解析原语）"两条路第 1 周并行验证；洗涤剂改自动投放 | HW | 立项后第 1 周 | open |
| R-24 | 硬件/安全 | 位控手臂做刚性接触（开关门、台面捏布、筒内）产生大内力，损坏本体或机器；力控未就绪（X-2） | 高 | 采集或评测中出现过流保护 / 机械损伤 | **2026-09-20 新增**。关节电流软件柔顺与碰撞保护；门与面板走解析原语；门磁吸、软垫台面、柔性指尖；遥操作端电流提示 | HW + TRAIN | A0 结束时 | open |
| R-25 | 数据 | 洗衣视频手部遮挡导致伪动作通过率低，每可用小时成本高于一般场景口径；人手策略不适用于二指夹爪（P-1、P-2） | 中 | 50 h 试购通过率 <30% | **2026-09-20 新增**。签大单前先试购实测；洗衣场景以 D1-H 真值为主 | CUR + TRAIN | 签约前 | open |

---

## 2. 未决决策登记（U）

| ID | 决策 | 当前倾向 | 裁决所需数据 | 裁决时点 | 不裁决的后果 | owner | 状态 |
|---|---|---|---|---|---|---|---|
| U-01 | recorder 中间件：dora-rs 节点 vs 自写采集循环 | 无；MCAP 落盘已定 | 多相机同步残差（目标 <1 ms 硬触发 / <5 ms 软同步，architecture §8.4）、断电落盘不丢 chunk（[recorder-sync-and-storage.md](recorder-sync-and-storage.md) §4 测试）、嵌入式 CPU 占用 <30% | M1 recorder 实现前两周做对比原型 | M1 阻塞 | DATA | open |
| U-02 | device 轨 ee_pose 60 Hz 与 100–200 Hz 约定冲突 | **已裁决 2026-09-08**：按传感器原生频率（≥50Hz）入湖，export 不上采；CLAUDE.md 决策 3 豁免 | — | — | — | DATA | closed |
| U-03 | 训练态依赖包：`lerobot-dataset` 独立包 vs `lerobot` 核心；MuJoCo 侧仿真现状 | **已裁决 2026-09-09**：训练态依赖改为 `lerobot` 核心包（≥0.6，锁版本），废弃 `lerobot-dataset`；Rerun .rrd 只作可视化缓存（决策 1 不变）；MuJoCo 侧仿真现状仍待查（转入 sim-track 调研项） | 安装后 API 核查报告；sim-track 调研 | M1 export 实现前 | export 选型返工 | DATA | closed（MuJoCo 项转 sim-track） |
| U-04 | 目标本体末端：三指简化 vs 五指 | 证据向三指倾斜，不站队 | TwinDEX 式四类任务（精细捏取/手内操作/工具使用/人机交互）消融，本体见 [robot-track-teleop.md](robot-track-teleop.md) §1 选型框架 | H1 中期（有本体后 3 个月内） | 槽位向量灵巧手段布局、P2 触发条件永远无法求值 | HW + TRAIN | open |
| U-05 | 具身转换阶段是否进架构 | **已裁决 2026-09-08**：进 architecture §2.3 作为可选阶段，仅穿戴/头戴 device 子形态触发 | — | — | — | CUR | closed |
| U-06 | P1 评估 Sunday 式手套 / P2 评估 TwinDEX 式外骨骼 | P1 评估手套；P2 触发依赖 U-04 | U-04 消融结果 + 手套自制原型的动作真值精度 | U-04 后 | 只能停在 UMI 平行夹爪覆盖面 | HW | open |
| U-07 | Fast-UMI 改型 | 先原版 UMI ×2 | SLAM 跟丢时长占比（device 质量门指标）**>10% 的 episode 超过 20%** 时触发评估；T265 替代方案（ZED Mini / 自算 VIO）先评 | H0 末看数据 | 弱纹理场景数据大批拒收 | HW | open |
| U-08 | P2 加 ToF 深度 / 眼动 | 砍掉，量产版再议 | 成本上限 +$30 BOM；眼动收益探针：注意力信号对子任务分割 F1 的提升 | P2 立项前 | 无（默认不加） | HW | accepted |
| U-09 | 腕带 EMG / 音频振动作为力信号代理 | **已裁决 2026-09-09**：两条都做——H1 同时跑 EgoTac 式视频推断力（L4 伪标签加 `tactile_pred` 槽位，provenance=inferred）与一次腕带 EMG/音频振动小实验，用决策 3 的 500 h 触觉 UMI 对照集作同一真值比较；P2 的 EMG 探针并入本项 | 与 device 轨软指形变（隐式力）配对采集 10 小时，看相关性 | H1 内一次小实验 | R-04 无前向对策 | HW | closed（H1 双探针） |
| U-10 | ORB-SLAM3（GPLv3）vs Basalt（BSD） | ORB-SLAM3 服务端限定 | 分发形态确认（SLAM 是否进设备固件）；Basalt 在 UMI 数据上的 ATE 对照 | H0 末 license 终审 | 商用发行 GPL 传染 | LEGAL + DATA | open |
| U-11 | license ⚠️ 待核查清单（22 项，见下表） | 非商用只进研究分支 | 逐项核查 | H0 末（M2 策展实现开始前）；P0 硬依赖项（GeoCalib/DroidCalib）**H0 开工前** | 违约风险 / 返工 | LEGAL | open |
| U-12 | Harmonic Reasoning 统一异步流 | 不抄；schema 声称两者都能消费 | 外生：细节披露；内生：写一个"连续时间流消费者"导出视图测试证明 schema 可吃（[data-format-contract.md](data-format-contract.md) §3.4） | 每半年复检 | 对冲宣称未验证 | TRAIN | open |
| U-13 | 观察名单：V-JEPA 2-AC、GR00T N2 统一动作空间 | 观察 | 外生 | 每半年复检 | — | TRAIN | open |
| U-14 | token→flow 切换成本 / 物理提示在 M 档涌现 / 相机系动作对移动底座 | 各有前置动作或 fallback（training-pipeline §5） | Stage B 前预演；fewshot-bench 曲线；通义处理不行退世界系 | Stage B 前 | Stage B 性能坑 | TRAIN | mitigating |
| U-15 | Stage A "显著优于零样本"的统计定义；held-out 机制早于 curation | held-out 已前置到 ingest 后（curation §8） | 显著性规则见 eval-protocol §4 | M1 export 实现时 | Stage A 放行不可判 | TRAIN | mitigating |
| U-16 | 质量门阈值"服从消融"但消融工具是 M3 交付物 | 过渡方案：M2 用版本化临时阈值 + 只标记 + 记漏斗（curation §1.2） | M3 mixture-runner | M3 | 阈值永远未裁决 | CUR | mitigating |
| U-17 | 去重 embedding 选型两文档相反 | **已裁决 2026-09-08**：SigLIP 起步，license 通过后升级视频模型（两文档已统一） | — | — | — | CUR | closed |
| U-18 | S0 数据腿范围：mocap 重定向数据属于哪条 track | 模型层不做 S0 已定；数据层裁决：mocap/重定向/神经轨迹归 **sim 轨**（`source` 子字段区分），见 [sim-track.md](sim-track.md) §6 | — | 已裁决 2026-09-08 | — | DATA | closed |
| U-19 | 里程碑命名冲突 | **已裁决 2026-09-08**：M1/M2/M3 工程按层；H0/H1/H2 硬件平台线；P0/P1/P2 硬件成熟度 | — | — | — | PM | closed |
| U-20 | 采用 SimFoundry 做 sim 轨场景来源与真机评测仿真替身 | 研究分支直接用；默认路径需换件（Hunyuan3D-2.1→TRELLIS.2、FoundationPose→待定、Gemini→本地 Qwen-VL、SAM3 条款审） | 换件后在自家 3 个任务复测 real2sim Pearson ≥0.8；U-11 新增 4 行核查 | M2 sim QC 实现前 | sim 轨场景只能手工建，评测无仿真替身 | TRAIN + LEGAL | open |
| U-21 | SimFoundry 规划轨迹（`planning_trace`）对 S2 长任务推理是否有收益 | 采用，但只作接地/校验语料，与真实标注混合 | 消融：S2 SFT 有/无 planning_trace，在长任务规划基准（eval-protocol §2）与真机长任务进度分上对比；模板化语言过拟合探针：held-out 真人指令改写集上的成功率差 | S2 首次 SFT（M3） | S2 语料只剩伪标签，无失败/重规划样本 | TRAIN | open |
| U-22 | Creator App 接入 SimFoundry 场景扫描（个性化任务 + 谓词验收） | **已裁决 2026-09-09**：H0 在研究分支用 SimFoundry 原版跑 10 个内部场景验证四个试跑指标；H1 对外以 U-20 换件后 Pearson ≥0.8 与 LEGAL 意见（U-29）为前提；家居孪生单独勾选同意（compliance §3） | 试跑指标：任务生成可用率（人工抽检通过 ≥80%）、谓词验收与人工判定一致率 ≥90%、每场景重建成本 ≤2.5 GPU·h；同意勾选率（拒绝率 >30% 则退回通用任务为主） | H1 前 | 任务市场停留在通用模板，多样性 KPI 靠 VLM 猜 | PLAT + CUR | closed（H0 试跑；H1 对外受 U-20 门控） |
| U-23 | 统一动作 schema：相机系相对末端 + 手部/夹爪状态作为四轨对齐目标，具身特异性进提示与掩码 | **已裁决 2026-09-09**：相机系相对末端 + 手部/夹爪状态为四轨公共动作目标；关节空间只在 L1 运动学门做一次性 IK 可行性标记；具身特异性进提示与掩码。落地位置：data-format-contract 0.3、curation §4.2、training-pipeline §1.2 | 契约 0.3 字段；伪标签 v0 在两种动作表示下的仿真收益对比 | M1 契约 0.3 前 | 伪标签、配方、具身转换各用各的动作空间 | DATA + TRAIN | closed |
| U-24 | 头戴设备量产是否冻结（P1 止步 EVT/DVT、H2 不做 PVT 500+ 台、P2 眼镜形态不立项） | **已裁决 2026-09-09**：冻结：P1 止步 EVT→DVT 参考设计并开源，不做 H2 的 PVT 500+ 台；P2 眼镜形态不立项；human 轨原始视频外购 + Creator App。H1 末按 G2（human 轨等小时消融）与 G3（外购 vs 自采 1.5×）复议。受影响条目待回写：R-04 EMG 探针并入 U-09；U-06/D-04 TwinDEX 评估改挂 U-04；U-08 视 P2 不立项处理；index-replica-plan §0/§1/§7/§8.2、program-plan §2/§4 H2 采集设备行、device-landscape §7.4 | 外购报价 ≤ 自采预估 ×(1/1.5)（0–3 月预判，与 G3 同阈值；6 月末用实测全成本复核）；human 轨等小时消融通过（G2） | 立即，H1 末复议 | $150–300k 沉没 + 硬件组分心 | HW + PM | closed（H1 末复议） |
| U-25 | 触觉/力/效应进契约的字段形态与采样约定 | **已裁决 2026-09-09**：进契约 0.3 作可空模态：tactile 存传感器无关 (N,6) 点集（对齐 LeRobot PR #4469）并可导出 observation.tactile.<name> [rows,cols]/[k,channels] 窗口；wrench 必带 frame_id；effort 标 measured/estimated；每路标 传感器家族/功能区/型号；MCAP 原生频率，export 窗口化。同时启动 500 h 触觉 UMI 对照集（阵列 + 光学并排共装，H1 启动、6–12 月完成）；是否进默认配方由对照集消融裁决（R-04 探针）；触觉切分按接触序列（RCT） | 500 h 触觉 UMI 对照集（R-04 探针）；上游 PR #4469 是否合并 | M1 契约 0.3（字段）；M2 末（是否进默认配方） | R-04 无探针；上游六个月未定格式 | DATA + HW | closed（字段）/ open（默认配方，M2 末） |
| U-26 | YD/T 6771-2026 八维质量标准全文与阈值、指定格式与元数据字段 | **部分裁决 2026-09-09**：八维报告器 v0（L1–L3 QC 输出 → 八维映射，维度名可重映射，阈值占位）于 2026-11-01 前交付（M1 内）；v1 待购得 YD/T 6770/6771 正文或 GB/Z 218.1 上线后对照阈值。**2026-09-09 补漏结果**：全文在标准平台因版权不公开（备案 108001-2026，三部分框架已由信通院确认）；网传阈值（缺失率 ≤5%、时间戳偏差 <20 ms、标注一致 ≥95%、≥480p/30fps、采集同步 ≤1 ms 与 <20 ms 互相矛盾）只作占位；并行标准：GB/Z 218.1-2026 / GB/Z 220-2026（2026-08-27，正文将上 openstd）、SJ/T 12250 报批稿、国家数据局系立项、ISO/CD 26264-1（30.60，数据集护照）；OpenLoong 无字段级 schema，事实布局为乐聚 LET（rosbag + HDF5 + 标记 JSON） | 购买 YD/T 6770/6771 文本；GB/Z 218.1 正文上线后做维度映射；2026-09-23 前向工信部标准体系指南提交意见 | 2026-11-01 实施前 | 中国大陆交付无验收依据（止损门 G6） | LEGAL + CUR | open |
| U-27 | 评测负责人先于采集扩张到岗；G1 门（分级得分与真机排序一致性 ≥0.9、序贯检验上线）不过不扩采集 | **已裁决 2026-09-09**：评测负责人列入首批招聘（0–3 月），先于采集扩张；G1 为交付门（分级得分协议 v1 + 序贯检验在 3 任务簇 × ≥3 策略变体上跑通并产出 run_id），不过则冻结采集扩量。program-plan §3 人力表待改招聘顺序 | 3 个任务簇真机基线 | 0–3 月 | 采集预算无法反向分配 | PM | closed |
| U-28 | 估值方法选型：PSD（零训练）/ SIEVE 式原语 medoid / ATHENA 影响函数 | **已裁决 2026-09-09**：PSD（零训练）M2 先上，SIEVE 式原语 medoid 第二，ATHENA 影响函数 M3 后；估值只作排序不作删除；G5 止损：估值 top-50% 训练不优于随机 50% 则回退 QC 门（R-16） | 估值 top-50% vs 随机 50% 训练对比 | M2 | 策展停留在 QC 门 | CUR | closed |
| U-29 | 默认路径资产许可核实与准入（2026-09-09 补漏检索结果） | **已裁决 2026-09-09**：拆表：M2 前 U-11 按 代码/权重/数据/骨干 四行重构。准入：不批量裁决，逐项由 LEGAL 出具意见——GR00T N1.7（NOML + gated 骨干）、Cosmos 3（OpenMDW-1.1，D-18 数据权利）、ABC-130K（Apache 但缺 LICENSE 文件）、ABC 代码 DINOv3；HumanNet/EgoLive/EgoSuite/HiPHI 在许可文本出现前不进入任何路径。意见出具前默认路径只用已核实 Apache/MIT 项，sim 轨微调基座与世界模型代理暂用研究分支 | U-11 表按 代码/权重/数据/骨干 拆行；NOML 义务（护栏终止、单方面更新、"Built on NVIDIA Cosmos"署名、每个 CI runner 接受）是否接受 | M2 前 | ⚠️待核查项混入默认配方 | LEGAL | mitigating（拆表 M2 前；准入逐项待 LEGAL） |
| U-30 | 元数据条件化（π0.7 路线）进配方 yaml 的字段集 | **已裁决 2026-09-09**：配方 yaml 新增 conditioning 段：quality_score、speed_band、track、outcome、source；推理时提示"高质量/正常速度/成功"；Stage B（S 档）起点配比 human ≥50% / device 20–30% / robot 10–15% / sim+WM ≤15%（D-15 口径，全部经缩放消融裁决）；有/无条件化消融为 Stage B 验收项之一 | Stage B（S 档）有/无条件化消融 | Stage B 前 | 低质/失败数据只能过滤不能利用 | TRAIN | closed（配比经消融复检） |
| U-31 | 真机评测农场 BOM 与规模（SO-101 / VLA-REPLICA 式，10–20 臂） | **已裁决 2026-09-09**：M3 建 10 臂（SO-101/VLA-REPLICA 式现货 BOM ≤$30k），先跑序贯检验与因子设计，吞吐不足再扩到 20；同时作为 PL4 的真机层 | 每评测活动真机试次需求（±2 点 ≈ 1,000 次量级，D-16） | M3 | 真机评测成为吞吐瓶颈 | TRAIN + HW | closed（M3 建 10 臂） |
| U-32 | 端上脱敏工具链选型与对伪标签的损伤基准 | **已裁决 2026-09-09**：端上脱敏默认开（EgoBlur 2.0 + 时序跟踪/人体轮廓补漏 + OCR 文本层 + 声纹 L1/L2）+ 入湖强制复检；对照集例外：受控场地、员工采集员、≥100 h，未脱敏帧在 L3 受限区限时保留、消融完成后删除，用于量化损伤（手部可见率、MPJPE 差、手-物接触一致性）并决定是否需要"脱敏前打标"窗口；compliance §3/§6/§9 待加该例外条款 | 脱敏前后伪标签对照集（≥100 h）；"脱敏前打标、脱敏后训练"两阶段是否必要 | H0 末 | R-18 无对策 | CUR + LEGAL | closed（对照集 H0 末交付） |
| U-33 | ego+exo 同步配对采集（Human-as-Humanoid 路线）是否进 H1 | **已裁决 2026-09-09**：H1 做 100 h 探针（受控场地固定机位，与 U-32 对照集共用采集员），用于重定向评测集与上身对齐消融；仿真收益显著再扩 | 上身控制器对齐动作块的仿真收益 | H1 前 | 人形上身对齐只剩单视角伪标签 | HW + TRAIN | closed（探针 H1） |
| U-34 | D1 触觉阵列与光学触觉传感器选型（并排共装、供应商、许可） | 指尖阵列 5×10 力矢量或 12×12 压力 + 一路光学式并排；存 (N,6) 点集；供应商待询价 ≥3 家（[capture-devices-design.md](capture-devices-design.md) §1） | 500 h 对照集的跨传感器迁移结果；单价与交期 | H1 EVT 前 | 触觉对照集只绑定单一型号 | HW | open |
| U-35 | D2 头戴 EVT 双目全局快门模组与 SoC 选型 | 双目灰度 1080p@60 全局快门 + 主 RGB 1440p@60；RK3588 级 SoC 只做编码/预检/脱敏；同步脉冲输出（capture-devices-design §2） | 手部可见率、同步残差、功耗与 4 h 续航实测 | H1 EVT 前 | EVT 规格漂移，配对采集无时钟源 | HW | open |
| U-36 | D4 数据手套选型：MANUS 级 vs 低成本 IMU 手套 | ≥200 Hz 为硬约束（T-800 >100 Hz 能量）；H0 先用 Quest 手追，H1 选型（capture-devices-design §4） | 手套↔本体复现的重定向误差；单价（$3–6k vs $300–800） | H1 前 | 逐指真值缺失，灵巧任务对齐集不可用 | HW + TRAIN | open |
| U-37 | 训练层是否纳入世界-动作模型（WAM）目标：next-frame 与 next-action 协同预测作为 Stage B/C 可选分支 | 已有 Dyna-2、NVIDIA DreamZero、AgiBot GE-Act 2.0、Cosmos Policy 四家独立验证，满足 CLAUDE.md 决策 7 的 ≥2 家门槛；倾向纳入为可选分支，不改数据层，只要求 export 保留连续帧对（research-dyna-comparison §8.1） | Dyna-2 "数据与目标都重要"消融的外部复现；自家 human 轨上 next-frame 协同 vs 仅 next-action 的消融 | 训练负责人 | M3 前 |
| U-38 | 消融切分器是否加「微调权重位移按模块分解」报告（Generalist 任务向量分析：ΔW 按传感/推理/执行分解，定位该多采哪类数据） | 训练层工具，属「数据层承载创新」的边界外；倾向 M3 作为可选报告，不进 M2 验收 | 自家 Stage B 微调实验上 ΔW 分解与采集干预的因果验证（research-four-routes §6.8） | TRAIN | M3 |
| U-39 | 是否立项 Dyna 复现 R0（≈$0.35–0.6M、6 个月、6 人）及视频扩散骨干选型（候选 A Cosmos 3 小杯 / 候选 B Wan 2.x） | **2026-09-20 范围收敛**：先执行 [dyna-replica-plan.md](dyna-replica-plan.md) §12（洗衣四任务、仅后训练 + VLM 大脑、自有人形 6 台，9 个月累计 ≈$0.55–1.05M），R0 降为 G-PA 不通过时的后备。原倾向：立项 R0：同时裁决 U-37、测出自家人→机器人迁移指数、完成 M3 训练栈约一半工程；骨干默认 A（已准入），B 待 U-11 核查后只进研究分支；R2 不自费（[dyna-replica-plan.md](dyna-replica-plan.md) §8） | 双臂同构工作站报价；Egocentric-10K 隐私门通过率；2B 档单卡推理实测频率；program-plan §4 Stage B 算力能否与 R1 合并 | 训练负责人 | M2 验收后、Stage B 开跑前 |
| U-40 | 预训练数据两轴配比：头戴视频伪动作 vs 与自研夹爪同构的手持采集器真值（D1-H）；前提是负责人 2026-09-20 确认"只服务自研本体，跨品牌本体不是目标" | 倾向两轴并进，主力模型按 10 万小时视频 + 8–10 万小时真值起步（[dyna-parity-fast-track.md](dyna-parity-fast-track.md) §2.3）；本产品线上 U-04 视为已定（二指力控夹爪），D1 直接做同构版（capture-devices-design §1.1） | 换算率四组对照实验：1 小时真值 ≈ 多少小时视频（零样本动作误差 + 叠 / 晾后训练成功率）；D1-H 轨迹复现成功率 ≥90% | 训练负责人 + HW | 立项后第 10 周 |
| U-41 | 上肢力控的上线窗口：交付一期间是否冻结控制器版本 | 倾向冻结，力控只在交付边界切换，切换后先跑新旧混训消融（[plans-review-hard-points.md](plans-review-hard-points.md) X-9） | 力控开发排期；新旧控制器下同一策略的成功率差 | 交付一批准时 | 交付中途动力学变化，已采数据变负资产 | 负责人 + HW | open（2026-09-20 新增，待领导拍板） |
| U-42 | 分筐方案 v1：筐数、"不可烘"单独成筐、小订单合并规则 | 倾向按试点方现行做法配置，"不可烘"洗前单独成筐或装网袋（S-1） | 试点方现行分筐做法、订单件数与件重统计 | 立项后第 1 周 | 洗后无法挑出不可烘衣物；小锅过多压低洗衣机利用率 | PM + TRAIN | open（2026-09-20 新增） |

### U-11 license 核查追踪表

| # | 模型/库 | 用途 | 已知状态 | 硬依赖阶段 | 核查状态 | owner |
|---|---|---|---|---|---|---|
| 1 | pyiqa（BRISQUE/NIQE） | 视觉质量 | 非商用 ⚠️ | — | 已排除，OpenCV BRISQUE 替代 | CUR |
| 2 | FAST-VQA / DOVER | 视觉质量 | 非商用研究许可 ⚠️ | — | 已排除 | CUR |
| 3 | HaMeR | 手部关键点 | MIT ⚠️待核查 | H0 伪标签 v0 | 待查 | LEGAL |
| 4 | WiLoR | 手部关键点 | 疑非商用 ⚠️ | — | 待查，默认不用 | LEGAL |
| 5 | HaWoR | 世界系手部轨迹 | ⚠️待核查 | H0 伪标签 v0 | 待查 | LEGAL |
| 6 | Dyn-HaMR | 世界系手部轨迹 | ⚠️待核查 | 备选 | 待查 | LEGAL |
| 7 | ORB-SLAM3 | device 轨位姿 | GPLv3 ⚠️ | P0 | 服务端限定使用，见 U-10 | LEGAL |
| 8 | MASt3R-SLAM | 弱纹理兜底 | ⚠️待核查 | H1 | 待查 | LEGAL |
| 9 | DPVO | 弱纹理兜底 | ⚠️待核查 | 备选 | 待查 | LEGAL |
| 10 | DROID-SLAM | 弱纹理兜底 | ⚠️待核查 | 备选 | 待查 | LEGAL |
| 11 | GeoCalib | 众包视频标定 | ⚠️待核查 | **P0 手机方案硬依赖** | 待查，H0 开工前 | LEGAL |
| 12 | DroidCalib | 众包视频标定 | ⚠️待核查 | **P0 手机方案硬依赖** | 待查，H0 开工前 | LEGAL |
| 13 | Depth Anything 大杯 | 单目深度 | 疑 CC-BY-NC ⚠️ | — | 默认用小/中杯（Apache） | CUR |
| 14 | InternVideo2 | 去重 embedding | 部分权重非商用 ⚠️ | 升级项 | 待查 | LEGAL |
| 15 | VideoMAE V2 | 去重 embedding | ⚠️待核查 | 升级项 | 待查 | LEGAL |
| 16 | MegaSAM | 世界系相机位姿 | ⚠️待核查 | H0 伪标签 v0 | 待查 | LEGAL |
| 17 | MoGe-2 | 稠密深度 | ⚠️待核查 | H0 伪标签 v0 | 待查 | LEGAL |
| 18 | Claude API（ToS） | VLM 仲裁 | 输出用于训练数据的条款未审 | M2 | 待查 | LEGAL |
| 19 | Hunyuan3D-2.1（SimFoundry 默认网格） | sim 轨场景重建 | 腾讯社区许可，EU/UK/韩国无授权 ⚠️ | U-20 | 默认换 TRELLIS.2（MIT） | LEGAL |
| 20 | FoundationPose / FoundationStereo / nvdiffrast | sim 轨位姿精修 | NVIDIA 非商用 ⚠️ | U-20 | 待找替代 | LEGAL |
| 21 | SAM3 | sim 轨分割 | Meta SAM License，非 OSS、gated ⚠️ | U-20 | 待查；SAM2 为 Apache 备选 | LEGAL |
| 22 | Gemini API（ToS） | SimFoundry VLM 阶段 | 输出用于训练数据条款未审 | U-20 | 默认换本地 Qwen-VL | LEGAL |
| 23 | GR00T N1.7 权重 | sim 轨微调基座 / 对照 | NVIDIA Open Model License（非 Apache；README 自相矛盾）⚠️ | U-29 | 研究分支；默认路径待裁决 | LEGAL |
| 24 | Cosmos-Reason2-2B（N1.7 骨干） | 同上 | NOML、gated 点击接受 ⚠️ | U-29 | 随 N1.7 | LEGAL |
| 25 | Cosmos 3（Edge/Nano/Super） | 世界模型代理 / 长尾合成 | OpenMDW-1.1（许可）；训练数据权利自述（D-18） | L5 | 可进默认路径 | LEGAL |
| 26 | HumanNet | human 轨伪标签模板 | 未发布、无 LICENSE ⚠️ | — | 不得引用为资产 | LEGAL |
| 27 | EgoLive（JD） | human 轨对照 | 无公开许可、JD Cloud gated ⚠️ | — | 排除 | LEGAL |
| 28 | EgoSuite-Open100K（光轮） | human 轨对照 | 自定义 "commercial-training-no-resale-v1.0" gated、文本未公布 ⚠️ | — | 排除直至文本公布 | LEGAL |
| 29 | Noitom HiPHI | sim 轨动捕重定向 | ModalityNet Open Research License v1.0：非商用、禁再分发、5 日删除 ⚠️ | — | 研究分支 | LEGAL |
| 30 | ABC-130K / ABC 训练代码（DINOv3） | 配方起点 / 参考基线 | 数据 Apache-2.0（LICENSE 文件缺失）；代码 Apache-2.0 但依赖 Meta DINOv3 许可 ⚠️ | L6 | 数据可用（固定 README 声明）；基线复现需审 DINOv3 | LEGAL |
| 31 | Wan 2.x 视频扩散骨干（1.3B / 5B / 14B） | Dyna 复现 WAM 骨干候选 B（dyna-replica-plan §4.1） | 许可未核查 ⚠️ | R0 | 待核查；核查前仅研究分支 | LEGAL |
| 32 | Build AI Egocentric-10K | Dyna 复现 R0 预训练语料（1 万 h 工厂第一视角） | 数据 Apache-2.0（HF 卡）；旁观者脱敏零说明 ⚠️ | R0 | 入湖先过隐私门；LEGAL 出具意见前不进默认配方 | LEGAL |

---

## 3. 自报数字登记（D）

"自报" = 公司官方/投资方口径，无独立复现。每条必须有"若不成立"分支与已有对冲；对冲写法模板：低成本预留接口 + 早期探针（training-pipeline §1.2-6 与 §5-2 的做法）。

| ID | 数字/宣称 | 来源属性 | 依赖它的设计 | 若不成立 | 对冲 / 探针 | 复检 |
|---|---|---|---|---|---|---|
| D-01 | Index 五阶段策展（五个名词） | Figure 官方，规则未公开 | curation 层骨架 | 阶段划分错，状态机/漏斗重排 | 各阶段方法全部来自可验证一手来源（Wall-OSS/Cosmos/Ego2Robot），五阶段正确性实质不依赖 Figure；状态机设计为可插拔 | 每次 Figure 新披露 |
| D-02 | "8 小时精策划即可出策略"、500h、60h vs 10h +58% | Figure 官方 | CLAUDE.md 决策 6（质量优先）、Stage A 10–50h 门槛 | 优先级排序失据；Stage A 长期不放行 | 第二锚点 GR00T 88h 真机、第三锚点 π0.5 目标域 2.4%；Stage A 放行不达时回退到"扩数据"分支 | Stage A 结果 |
| D-03 | 采集效率 PrimeU 4.8–7.2×（学术实测，人类视频）与 TwinDEX 5.3×（自报，外骨骼） | 混合；两者形态不同，**不是互证** | H1 成本验收 <1/5（中间检查点 1/3） | 成本验收失守 | R-02 止损阈值；每季度实测自家倍率替换外部数字 | 每季度 |
| D-04 | TwinDEX "几百条完成后训练"、无本体≈遥操等效 | 公司自报 | 采集矩阵 TwinDEX 行、P2 演进 | robot 轨遥操预算不能降 | 已降权（隐含 WALL 基座）；P2 触发条件依赖自家消融 U-04 | U-04 后 |
| D-05 | Sunday ACT-2 99.1%、Skill Transform 90%+、$200/$400 | 公司/投资方自报，两来源单价不一致 | 采集矩阵手套行、具身转换阶段 | 90% 若为 60%，该档位产出率崩塌 | 具身转换有专属质量门，失败只标记；P1 先自制 5 只手套实测转换成功率再决定量产 | P1 评估 |
| D-06 | Generalist 50 万+h、物理提示 59%/83%、64%→99% | 公司自报 | 演示库为一等产物、fewshot-bench、demo 槽位接口 | 演示库切片/质量位成沉没成本 | 接口预留零成本；fewshot-bench 从 Stage B 起持续测不等 L 档 | Stage B 起每版本 |
| D-07 | GEN-0 骨化相变（1B/6B/7B+）、L(D) 幂律 | 单家博客，无复现 | S/M/L 规模阶梯触发门槛、scaling-fitter | 阶梯门槛失据 | Lin et al. 学术幂律作独立印证（度量不同）；scaling-fitter 用自家曲线替换外部门槛 | 每次数据翻倍 |
| D-08 | Index 30 分钟/秒、1,600 万条、4.4 万周活 | Figure 官方；**通过率无来源** | 众包可行性、H0 验收分母 | 验收分母虚 | H0 用自家漏斗实测通过率反推原始时长需求 | H0 末 |
| D-09 | 多样性 KPI 373/1,146/116 每 1,000h | Figure 官方；分母口径与计数定义未公开 | curation KPI、H1 验收 | H1 无法验收 | H1 改用相对值（环比提升）；计数定义自定于 eval-protocol | H1 |
| D-10 | 通义线下 slide（数据管线六步、80 维、CaPE、prompt 模板） | 非公开材料；§1 有 Ego2Robot 论文交叉，§3/§4 单家 | curation 两个一致性门、cleaning 选型、training §1.2 三条架构决策 | 与"≥2 家共识"原则冲突 | 训练层三条标为"单家实践，Stage B 前需第二来源或自家消融"；数据管线部分已有论文佐证 | 通义正式发布时 |
| D-11 | Ego2Robot 放大倍数 | 论文 + slide | 伪标签工厂预期产出 | — | **已统一 2026-09-08**：1,933h→24,808h（≈12.8×），arXiv:2608.02580 | closed |
| D-12 | 遥操作硬件 Quest 3/OpenTeach | **自选，非 Figure 方案**（Figure 未披露） | robot 轨采集 | — | 明确该决策与"对标 Figure"无关，不得以 Figure 为由加固 | — |
| D-13 | WGO-Bench：VLM 子任务标注端到端 F1 0.168、$2.64/h（人工 1/19） | 供应商博客（Macrodata），单家 | L3 的 VLM 分层门阈值（F1 ≥0.6 自动通过）；P3 定价 | 自家 VLM 标注更差 → 人工比例升、P3 毛利降 | 自家任务簇上抽检 F1 后再定阈值 | M2 |
| D-14 | Label Studio 元分析：5% coreset ≈ 85–90%、0.31% 投毒 → 98–99% 后门 | 供应商综述（1,228 篇），未逐篇核 | L3 估值排序器优先级；投毒防御含世界模型路径 | coreset 效果不成立 → 估值线降级（止损门 G5） | 自家消融 | M3 |
| D-15 | 配比：GigaBrain-0.7 真机 55%/UMI 22%/ego 8%/sim+WM 15%；Xiaomi-Robotics-1 10 万 h UMI + 1 万 h；Riemann 200K h ego / 3 h 每真机任务 | 论文自报，无复现 | L6 配方起点（human ≥50% / device 20–30% / robot 10–15% / sim+WM ≤15%） | 配比不适用自家规模 | 全部经缩放消融裁决；斜率为零的轨停扩 | Stage B |
| D-16 | RoboLab：70 次 90% 成功率 CI 80.5–95.9；±2 点需 ~1,030 次 | NVIDIA 博客（二项式计算可复核） | L7 评测 N；U-31 农场规模 | — | 序贯检验（TRI）与主动因子设计降低 N | M2 |
| D-17 | AgiBot World 2026 第三期 wrench/effort"必填" | 第三方转述；公开 HF 卡片字段表只见关节位置/速度与末端位置 | U-25 字段形态参考 | 无影响（字段形态另有 PR #4469/PRISM 依据） | 开 tarball info.json 核实后更新 | M1 |
| D-18 | Cosmos 3 训练数据"NVIDIA 自有 + 商用许可公开数据" | NVIDIA 模型卡自述，无清单；OpenMDW-1.1 把第三方权利清理推给使用者 | L5 世界模型代理基座 | 输出含权利瑕疵 → 代理只用于评测不用于训练数据 | 生成数据 lineage `synthetic=true` 且不进对外数据集 | 每次 Cosmos 版本 |
| D-19 | Figure Index：16M 视频、44k WAU、$15M 已付、373 任务/1,146 物体/116 环境 per 1,000 h；官方文与 App Store 隐私标签无旁观者脱敏声明，人工审核在用户级看原始样本 | Figure 官方博客 + Humanoids Daily 转述；无第三方复现 | index-replica-plan 对标基线；compliance 差异化设计（审核员只见脱敏流、上传即脱敏） | Index 若已做脱敏则差异化点消失（合规仍必需） | 差异化不依赖 Index 是否脱敏；数字只作分母量级 | H1 |
| D-20 | Gemini Robotics 2：新具身 <200 条示范/数小时适配 | DeepMind 官方博客自述 | 北极星 24 个月目标（≤5 真机小时）量级 | 目标量级失据 | 目标为占位，M2 初按自家曲线重定；Riemann "3 h/任务"（论文）作第二锚点 | M2 |
| D-21 | Dexset：操作员 $28–60/h、熟练 25–40 vs 新手 8–12 可用集/h、QA 拒收 10–30% | 供应商博客，"来自自有采集车间"，带营销目的 | §1.2 遥操作成本基线、robot 轨 ≤$100/h 目标、H1 "< 遥操作 1/5" 判据的分母 | 分母偏低或偏高一档 | H0 完成 ≥3 家询价后以询价替换；RCSV $118/h 作第三方交叉 | H0 末 |
| D-22 | Dyna-2：1K→1M h 人类视频幂律（零样本机器人 Acc@0.5 0.067→0.159、MSE 0.180→0.117，指数 +0.139/−0.0713）；后训练 20→53%；客户质检 46→87%；1.55× vs DYNA-1；约 10 min 拧瓶盖；joint 目标 39/39 任务胜 action-only | dyna.co 研究页一手（2026-09-14 curl 核对，修正了第三方转述的 6.3→16.4% 与 13 min）；单实验室 14 任务、每任务 10 次盲测、VLA 基线按 VLA 管线调参、无同行评审 | 战略 §1.1 "人类视频为预训练主轴"、U-37 WAM 分支 | 主轴判断仍有 HumanScale/ZimaBlue/GR00T N1.7 支撑；U-37 退回可选实验 | 抓到一手研究页后核对指数；G2 自家 human 轨缩放消融 | G2 |
| D-23 | Skild S1：未见任务逐步成功率 66% vs 语言 VLA 9%（10 万 h）、seen 任务 96%；1 条上下文演示 ≈ 380 条后训练 episode（50–100 h 遥操作），2,000 条后 VLA 86%；$1 采集配 $3 质控 | **2026-09-14 改为一手**：skild.ai S1 博客原文（sources/skild/s1.txt）；内部基准、4–8 分钟长程任务、失败后人工干预继续累计逐步成功率、训练方法未披露 | eval-protocol 少样本三刻度与 L1–L5 扰动阶梯；program-plan 策展/采集预算比 | 预算比按自家 G2 数据重定；换算只作量级 | G2 前用自家数据复核质控比 | G2 |
| D-24 | Generalist GEN-1：三任务 99%（GEN-0 64%、无预训练 19%）；每任务 ~1 h 机器人数据；50 万 h 无机器人数据预训练；速度 ~3× π0/π*0.6 | 官方博客一手，自报；参数量/算力未披露 | 战略 §2.3 北极星 12/24 月目标量级；D-07 补充 | 北极星目标为占位（同 D-20） | M2 初按自家曲线重定 | M2 |
| D-25 | Sunday ACT-2：泛化差距（域内−域外）随预训练规模 82→10→8→4→0；高质量子采样 12.5%/25%/50% → 75.6/87.9/92.3% vs 均匀 43.8/53.6/64.1%；785 次 99.1%±0.3、每户零适配；单条示例 SFT 教会可泛化折法 | sunday.ai ACT-2 预览一手（2026-09-14 curl）；自评标注（两轮独立、评分表事前固定）、单任务族、模型架构与数据小时数未披露 | eval-protocol 泛化差距指标与 Solve 声明格式；curation §7 高质量子采样消融目标量级；L3 估值排序器（D-14）价值预期 | 策展增益量级不复现 → 估值线降级（G5） | 自家 human/device 轨复现同一消融，目标只作量级 | M2 |
| D-26 | Dyna 生产指标：DYNA-1 35 条/h、75% 达标 → DYNA-2 95 条/h、93% 达标（1,590/天）；新站点 3 天达 ROI；车队每站每天 >1 TB；鼎泰丰全门店扩张、2027 上半年数百台 | dyna.co《Not Just a Model, But a Product》一手；首页 KPI（100/180/200 件/h、≥98%、<90 s、±2 mm）自 2026-09-16 起为 dyna.co 首页一手（sources/dyna/home.txt）；单客户单任务族，无第三方 | data-platform 容量模型（1 TB/站/天）；R-20 飞轮反证的对照面；D5 触发式固化「两家验证」状态 | 容量模型分母偏高一档 | 容量按自家 D5 码率重算；D5 状态不依赖 Dyna 商业数字 | M3 |
| D-27 | Figure 产能与车队：350+ 台 F03、1 台/小时、末端首检良率 >80%、电池线 99.3%、9,000+ 执行器；BMW 1,250 h / 9 万件 / 3 万台 X3、KPI 84 s / >99% / 零干预；Index 周活 69,943、35 min/s（第三方 ⚠️） | figure.ai 一手（产能、BMW）；Humanoids Daily 转述（周活） | 战略 §1.1 对标分母；robot-track-teleop §6 车队 KPI 模板（周期/精度/干预三项） | 无设计依赖，仅作量级 | — | H1 |

---

## 4. research → 设计 回灌清单

每份 research 文档新增或修改后，对照下表检查其结论是否已进入对应设计文档；未进入的在 R-12 下开条目。

| research 文档 | 回灌目标 | 最近一次同步 |
|---|---|---|
| research-figure.md | architecture §1–§2、CLAUDE.md 决策 3/6 | 2026-09-14（一手补充指向 research-four-routes §1） |
| research-opensource.md | architecture §7 选型、CLAUDE.md 决策 1/5 | 2026-09-08（版本回填、DexMimicGen） |
| research-generalist-dora.md | architecture §6.5、index-replica-plan §1.0、training §1.2-6 | 2026-09-14（一手补充指向 research-four-routes §4） |
| research-vla-pretraining.md | training-pipeline §1.1/§2、curation §5 | 2026-09-08（Stage/阶段命名与档位门槛统一） |
| research-qwen-robotics.md | curation §1.4b/§4.1、cleaning §1.6–1.7、training §1.2 | 2026-09-08（Ego2Robot 数字统一） |
| research-sunday.md | architecture §2.3、index-replica-plan §1.0、device-track-umi §4 | 2026-09-14（ACT-2 一手补充指向 research-four-routes §3） |
| research-twindex.md | index-replica-plan §1.0、device-landscape §5、U-04 | 2026-09-04 |
| device-landscape.md | index-replica-plan §1、robot-track-teleop §1 | 2026-09-04 |
| research-simfoundry.md | sim-track §1–§3/§5、eval-protocol §2/§5、governance U-20/U-11 | 2026-09-09 |
| research-skild.md | governance D-23（已改一手）；eval-protocol §3（L1–L5 扰动阶梯、干预记账，待 M2）；device-track-umi §0（Skild 三轴表引用，待 M1）；data-format-contract 秒级切片含 human 轨（待契约 0.3） | 2026-09-14（登记，设计文档待 M1/M2） |
| research-four-routes.md | governance U-38/D-25–D-27（已登记）；eval-protocol §1/§3（泛化差距、Solve 声明、槽位探针、反向 KL）；curation §4.1/§7（失败模式本体、高质量子采样消融）；robot-track-teleop §1/§6 + data-format-contract（视觉自标定、hardware_health）；capture-devices-design D5 状态（已改） | 2026-09-14（登记 + D5 状态，其余待 M2） |
| research-dyna-comparison.md | governance U-37/R-20/D-22–D-24（已登记）；training-pipeline §2 WAM 分支；data-format-contract §3 连续帧对与 grasp_aperture；eval-protocol §3 少样本三刻度；program-plan §4 质控预算比 | 2026-09-14（登记，设计文档回写待 M2/M3） |
| data-strategy-roadmap.md（战略层，含 225 条扫描证据） | 回写清单见其 §7.2：data-format-contract（契约 0.3）、curation（段级/估值）、architecture §2.3、sim-track（优先级）、training（conditioning）、eval-protocol（分级/序贯/代理）、compliance（脱敏前置/同意图）、program-plan（组织/预算/止损门）；本次已改 research-opensource、research-generalist-dora、U-03、R-10 | 2026-09-09 |
