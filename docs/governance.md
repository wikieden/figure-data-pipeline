# 治理登记：风险 · 未决决策 · 自报数字

> 2026-09-08 建立，来源为全局 review 三路审计（一致性 / 覆盖缺口 / 风险与未决项）的合并结果。三张表是活文档：每条有 owner（按角色，非人名）与复检时点；状态字段只有 `open / mitigating / closed / accepted`。新增风险、新增依赖他家数字的设计决策、新增待裁决项都必须先在这里登记再写进设计文档（CLAUDE.md 约定）。

角色缩写：**DATA** 数据层（recorder/ingest/export/schema）、**CUR** 策展层、**TRAIN** 训练层、**HW** 采集硬件、**PLAT** 数据平台/运维、**LEGAL** 法务合规、**PM** 项目管理。

---

## 1. 风险登记（R）

| ID | 类别 | 风险 | 严重度 | 触发条件 / 观测信号 | 对策 | owner | 复检 | 状态 |
|---|---|---|---|---|---|---|---|---|
| R-01 | 合规 | 隐私合规：进家庭众包采集；"raw 永存"与存储限制原则冲突；误模糊不可逆 | 高 | 任一区域上线前；误模糊率 >0.1% | [compliance-and-security.md](compliance-and-security.md)：保留期政策、DPIA 触发条件、删除 SLA、误模糊率进 QC、脱敏前哈希留存 | LEGAL | H0 末、每季度 | mitigating |
| R-02 | 经济 | 单位经济不成立：每可用训练小时全成本长期高于遥操作 | 高 | 连续两季度 > 遥操作 1/2 且不降 | 止损阈值写入 index-replica-plan §8.4；容量/成本模型 [data-platform.md](data-platform.md) §1；存储成本纳入 | PM | 每季度 | open |
| R-03 | 诚实性 | 采信他家自报数字而无对冲；对外宣称不可复现 | 中 | 设计决策引用未登记数字 | 本文 §3 D 表 + CLAUDE.md 钩子；对外宣称附可复现日志与干预率（[eval-protocol.md](eval-protocol.md)） | PM | 每次新增 research 文档 | mitigating |
| R-04 | 数据 | human 轨无触觉/力学，接触密集任务天花板未知 | 中 | fewshot-bench 在接触密集任务簇上 human 轨增量 ≈0 | 定位为规模腿；robot/device 轨封顶；探针：按任务簇拆分的 human 轨增量消融（eval-protocol §3）；P2 探索 EMG/音频代理（未验证） | TRAIN | Stage B 起每数据版本 | accepted |
| R-05 | 平台 | 众包欺诈；漏检率无 ground truth | 中 | 欺诈率 >1% 或漏检率不可测 | 红队植入测试集（每月投放已知欺诈样本测漏检率，[data-platform.md](data-platform.md) §5）；计酬锚定通过分钟 | PLAT | 每月 | mitigating |
| R-06 | 数据 | 伪标签质量上限；六因子质量分公式未验证 | 高 | 金标准配对集 Spearman <0.5；H0 "伪标签→仿真收益"不见收益 | curation-pipeline §7 增加公式验收；H0 止损门；金标准来源与规模在 [sim-track.md](sim-track.md) §6 动捕条目 | CUR | H0 末 | open |
| R-07 | 硬件 | 设备标定漂移与 GoPro 时戳抖动导致大批拒收 | 中 | `flag:calib_stale` 或 `reject_timing` 占比 >5% | architecture §8.5 在线再估计 + 待重标队列；ingest 先实测 GoPro 抖动分布再定阈值（[ingest-spec.md](ingest-spec.md) §2） | DATA | M1 ingest 实现时 | open |
| R-08 | 流程 | 调研证据链不完整：research-opensource 由挂起 agent 的 13 组结果综合；architecture 对抗核查未完成；Generalist/TwinDEX 官网抓取受限 | 中 | 选型依赖单一来源 | 补做清单：lerobot-dataset API 面核查（M1 export 前）、MuJoCo 侧仿真现状（sim-track）、Foxglove 转型影响评估；单来源论断保持 ⚠️ 标注 | PM | M1 末 | open |
| R-09 | 依赖 | 商业 VLM API 在数据生产关键路径：可用性、版本漂移无权重哈希、输出用于训练数据的条款未审 | 中 | API 不可用 >1h；API 版本变更 | 本地 Qwen-VL 主力，API 只做分歧仲裁且可降级；lineage 记模型名+API 版本+日期（cleaning-algo-selection 纪律 4）；ToS 进 license 终审 | CUR + LEGAL | H0 末 | mitigating |
| R-10 | 依赖 | 上游生态单点：LeRobotDataset v3 唯一训练格式；MCAP/Foxglove 生态方向变化 | 低 | lerobot-dataset 破坏性版本；MCAP 维护停滞 | uv.lock 锁版本并在 research-opensource 回填；export 层抽象 writer 接口（[data-format-contract.md](data-format-contract.md) §4）；MCAP 规范本身开放，可自维护 reader | DATA | 每半年 | accepted |
| R-11 | 合规/安全 | 人口与地域偏差；按分钟计酬的用工性质；上门服务人身安全；上传内容安全 | 中 | 再平衡簇覆盖按地域/人群严重不均；任一区域劳动法咨询意见为"雇佣" | 再平衡加操作者轴（curation §2.2）；劳动合规、背景审查、内容安全流程在 [compliance-and-security.md](compliance-and-security.md) §7–§9 | LEGAL + PLAT | H1 前 | open |
| R-12 | 流程 | 文档同步失效：research 新发现不回灌总设计（Ego2Robot 三套数字、具身转换未进架构、embedding 选型两文档相反、GPL 未传导） | 中 | 同一事实两处不一致 | docs/README.md 索引 + "research → 设计"回灌清单（§4）；每份 research 文档末尾必须有"已同步到"行；CI 链接扫描 | PM | 每次 review | mitigating |
| R-13 | 流程 | 设计-实现漂移无追踪 | 低 | 设计写明"已落地"但代码无 | training-pipeline §4 状态列；architecture §7 能力→模块表；测试基线（schema 兼容、CLI smoke、golden fixture） | DATA | 每里程碑 | mitigating |

---

## 2. 未决决策登记（U）

| ID | 决策 | 当前倾向 | 裁决所需数据 | 裁决时点 | 不裁决的后果 | owner | 状态 |
|---|---|---|---|---|---|---|---|
| U-01 | recorder 中间件：dora-rs 节点 vs 自写采集循环 | 无；MCAP 落盘已定 | 多相机同步残差（目标 <1 ms 硬触发 / <5 ms 软同步，architecture §8.4）、断电落盘不丢 chunk（[recorder-sync-and-storage.md](recorder-sync-and-storage.md) §4 测试）、嵌入式 CPU 占用 <30% | M1 recorder 实现前两周做对比原型 | M1 阻塞 | DATA | open |
| U-02 | device 轨 ee_pose 60 Hz 与 100–200 Hz 约定冲突 | **已裁决 2026-09-08**：按传感器原生频率（≥50Hz）入湖，export 不上采；CLAUDE.md 决策 3 豁免 | — | — | — | DATA | closed |
| U-03 | lerobot-dataset 包 API 面、MuJoCo 侧仿真现状未查证 | 以实际安装为准 | 安装后 API 核查报告；sim-track 调研 | M1 export 实现前 | export 选型返工 | DATA | open |
| U-04 | 目标本体末端：三指简化 vs 五指 | 证据向三指倾斜，不站队 | TwinDEX 式四类任务（精细捏取/手内操作/工具使用/人机交互）消融，本体见 [robot-track-teleop.md](robot-track-teleop.md) §1 选型框架 | H1 中期（有本体后 3 个月内） | 槽位向量灵巧手段布局、P2 触发条件永远无法求值 | HW + TRAIN | open |
| U-05 | 具身转换阶段是否进架构 | **已裁决 2026-09-08**：进 architecture §2.3 作为可选阶段，仅穿戴/头戴 device 子形态触发 | — | — | — | CUR | closed |
| U-06 | P1 评估 Sunday 式手套 / P2 评估 TwinDEX 式外骨骼 | P1 评估手套；P2 触发依赖 U-04 | U-04 消融结果 + 手套自制原型的动作真值精度 | U-04 后 | 只能停在 UMI 平行夹爪覆盖面 | HW | open |
| U-07 | Fast-UMI 改型 | 先原版 UMI ×2 | SLAM 跟丢时长占比（device 质量门指标）**>10% 的 episode 超过 20%** 时触发评估；T265 替代方案（ZED Mini / 自算 VIO）先评 | H0 末看数据 | 弱纹理场景数据大批拒收 | HW | open |
| U-08 | P2 加 ToF 深度 / 眼动 | 砍掉，量产版再议 | 成本上限 +$30 BOM；眼动收益探针：注意力信号对子任务分割 F1 的提升 | P2 立项前 | 无（默认不加） | HW | accepted |
| U-09 | 腕带 EMG / 音频振动作为力信号代理 | 探索项 | 与 device 轨软指形变（隐式力）配对采集 10 小时，看相关性 | H1 内一次小实验 | R-04 无前向对策 | HW | open |
| U-10 | ORB-SLAM3（GPLv3）vs Basalt（BSD） | ORB-SLAM3 服务端限定 | 分发形态确认（SLAM 是否进设备固件）；Basalt 在 UMI 数据上的 ATE 对照 | H0 末 license 终审 | 商用发行 GPL 传染 | LEGAL + DATA | open |
| U-11 | license ⚠️ 待核查清单（17 项，见下表） | 非商用只进研究分支 | 逐项核查 | H0 末（M2 策展实现开始前）；P0 硬依赖项（GeoCalib/DroidCalib）**H0 开工前** | 违约风险 / 返工 | LEGAL | open |
| U-12 | Harmonic Reasoning 统一异步流 | 不抄；schema 声称两者都能消费 | 外生：细节披露；内生：写一个"连续时间流消费者"导出视图测试证明 schema 可吃（[data-format-contract.md](data-format-contract.md) §3.4） | 每半年复检 | 对冲宣称未验证 | TRAIN | open |
| U-13 | 观察名单：V-JEPA 2-AC、GR00T N2 统一动作空间 | 观察 | 外生 | 每半年复检 | — | TRAIN | open |
| U-14 | token→flow 切换成本 / 物理提示在 M 档涌现 / 相机系动作对移动底座 | 各有前置动作或 fallback（training-pipeline §5） | Stage B 前预演；fewshot-bench 曲线；通义处理不行退世界系 | Stage B 前 | Stage B 性能坑 | TRAIN | mitigating |
| U-15 | Stage A "显著优于零样本"的统计定义；held-out 机制早于 curation | held-out 已前置到 ingest 后（curation §8） | 显著性规则见 eval-protocol §4 | M1 export 实现时 | Stage A 放行不可判 | TRAIN | mitigating |
| U-16 | 质量门阈值"服从消融"但消融工具是 M3 交付物 | 过渡方案：M2 用版本化临时阈值 + 只标记 + 记漏斗（curation §1.2） | M3 mixture-runner | M3 | 阈值永远未裁决 | CUR | mitigating |
| U-17 | 去重 embedding 选型两文档相反 | **已裁决 2026-09-08**：SigLIP 起步，license 通过后升级视频模型（两文档已统一） | — | — | — | CUR | closed |
| U-18 | S0 数据腿范围：mocap 重定向数据属于哪条 track | 模型层不做 S0 已定；数据层裁决：mocap/重定向/神经轨迹归 **sim 轨**（`source` 子字段区分），见 [sim-track.md](sim-track.md) §6 | — | 已裁决 2026-09-08 | — | DATA | closed |
| U-19 | 里程碑命名冲突 | **已裁决 2026-09-08**：M1/M2/M3 工程按层；H0/H1/H2 硬件平台线；P0/P1/P2 硬件成熟度 | — | — | — | PM | closed |

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

---

## 4. research → 设计 回灌清单

每份 research 文档新增或修改后，对照下表检查其结论是否已进入对应设计文档；未进入的在 R-12 下开条目。

| research 文档 | 回灌目标 | 最近一次同步 |
|---|---|---|
| research-figure.md | architecture §1–§2、CLAUDE.md 决策 3/6 | 2026-09-08（Figure 03 数字回填 §5） |
| research-opensource.md | architecture §7 选型、CLAUDE.md 决策 1/5 | 2026-09-08（版本回填、DexMimicGen） |
| research-generalist-dora.md | architecture §6.5、index-replica-plan §1.0、training §1.2-6 | 2026-09-04 |
| research-vla-pretraining.md | training-pipeline §1.1/§2、curation §5 | 2026-09-08（Stage/阶段命名与档位门槛统一） |
| research-qwen-robotics.md | curation §1.4b/§4.1、cleaning §1.6–1.7、training §1.2 | 2026-09-08（Ego2Robot 数字统一） |
| research-sunday.md | architecture §2.3、index-replica-plan §1.0、device-track-umi §4 | 2026-09-08（具身转换进架构） |
| research-twindex.md | index-replica-plan §1.0、device-landscape §5、U-04 | 2026-09-04 |
| device-landscape.md | index-replica-plan §1、robot-track-teleop §1 | 2026-09-04 |
