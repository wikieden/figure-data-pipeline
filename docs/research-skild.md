# Skild AI 一手调研：Skild Brain / 全身体（omni-bodied）/ S1 上下文学习（2026-09-14）

> 来源规则同 [research-four-routes.md](research-four-routes.md)：每条事实指向 [docs/sources/skild/](sources/MANIFEST.md) 的归档原文（skild.ai 全部 11 篇博客，2024-07-09 至 2026-09-10，2026-09-14 curl 直抓）。记法 `[K:slug]` = `sources/skild/slug.txt`。此前 [research-dyna-comparison.md](research-dyna-comparison.md) §4 的 Skild 数字来自第三方转述，本文已逐条对照一手页核实；governance D-23 改为一手。全部性能数字为公司自报，内部基准，无独立复现。

[K:series-a]: sources/skild/announcing-our-300m-series-a.txt
[K:brain]: sources/skild/building-the-general-purpose-robotic-brain.txt
[K:loco]: sources/skild/one-policy-all-scenarios.txt
[K:omni]: sources/skild/omni-bodied.txt
[K:watching]: sources/skild/learning-by-watching.txt
[K:series-c]: sources/skild/series-c.txt
[K:bengaluru]: sources/skild/bengaluru.txt
[K:oem]: sources/skild/reindustrial-revolution.txt
[K:zebra]: sources/skild/skild-zebra.txt
[K:s1]: sources/skild/s1.txt
[K:arr]: sources/skild/skild-crosses-100m-arr.txt

## 0. 值得提的六件事

1. **S1 把"任务用视频指定、不用语言"做成了主路线**，且是四家之外唯一把 ICL 做到**未见任务 + 10 分钟长程**的：unseen 任务 ICL 66% vs 语言提示 VLA 9%（10 万 h 预训练），seen 任务 96% vs VLA 更低；差距"随预训练数据指数级拉大" [K:s1]。Generalist GEN-1.5 与 RoboTTT 被它点名为"短视野或分布内" [K:s1]。
2. **它是唯一把 UMI 列进自家数据源矩阵的头部厂商**："Skild has been scaling all of them in-house"，四源三轴表里 UMI 三项都是 Moderate [K:s1]。这是本仓库 device 轨的直接外部佐证。
3. **"每花 $1 采数据就花 $3 做质控"现在是一手原句**："For every dollar we spend on collecting data, we spend three on quality control. Every data point entering pre-training is screened for low-level precision, task coherence, and annotation fidelity" [K:s1]。
4. **评测协议有两处可直接借用**：L1–L5 扰动阶梯（15 cm/30° → 30 cm/45° → 同可供性换物 + 15 cm 垂直 → 半数动作换臂）[K:s1]；长程任务用"人工干预恢复后继续累计逐步成功率"，并明说干预主要给 VLA 基线，"否则基线得零分" [K:s1]。
5. **1 条演示 ≈ 380 条后训练 episode**的换算有完整实验设定：VLA 用 1–2,000 条遥操作后训练未见任务，交点靠插值；380 条 4–10 分钟长程演示要 50–100 h 遥操作；2,000 条后 VLA 86% 反超单条 ICL 66% [K:s1]。
6. **商业与飞轮口径**：首次商业部署 10 个月后 ARR 破 $100M、60+ 付费客户、约 90% 收入来自操作、10% 移动（AMR 4%）[K:arr]；Series C $1.4B、估值 >$14B [K:series-c]；收购 Zebra（前 Fetch）机器人部门 [K:zebra]；ABB / UR / MiR OEM 合作与 Foxconn Blackwell 装配线 [K:oem]。飞轮观点与 Dyna 的 R-20 反证互补："部署数据对已掌握该任务的专才价值很小，价值在于把多个专才的数据带回通才"（"Physical RSI"）[K:arr]。

## 1. 时间线

| 日期 | 事件 | 技术要点 | 来源 |
|---|---|---|---|
| 2024-07-09 | 出隐身，Series A $300M，估值 $1.5B | "trained on an unparalleled scale of data"；跨具身（四足、人形、桌面臂、移动操作） | [K:series-a] |
| 2025-07-29 | 《Building the general-purpose robotic brain》 | Skild Brain **分层**："(1) a low-frequency high-level manipulation and navigation action policy which provides inputs to a (2) high-frequency low-level action policy"；"more than just a VLM in disguise"，批评"VLM + <1% 机器人数据"路线缺"grounded actionable information"；规模观："achieving scale requires collecting trillions of examples"，靠"large-scale simulation and internet video data to pre-train"，"post-train… using targeted real-world data"；训练集含人类数据（"humans are also a form of robot!"） | [K:brain] |
| 2025-08-06 | 端到端视觉行走 | 低层策略"From raw images and joint feedback, the model directly outputs low-level motor commands"，无地图无规划无模式切换；楼梯比脚深 3 cm 仍精确落脚 | [K:loco] |
| 2025-09-24 | 全身体大脑 | "We created a universe with 100,000 different robots and trained our AI to control them all"；测试机器人全部不在训练集；断腿 / 锁膝 / 卡轮 / 高跷 零样本适应；失败后把上一次试验放进提示第三次成功 → 运动的上下文学习（LocoFormer） | [K:omni] |
| 2026-01-12 | 看视频学 | 遥操作两大死穴：多样性（困在实验室）与规模（实时、不可能到万亿 token）；"finetune our model to perform new skills by watching videos alone, and only a small amount of robot data (<1 hr)" | [K:watching] |
| 2026-01-14 | Series C $1.4B，>$14B | 四类数据源定型：预训练 = 大规模仿真（"trillions of synthetic experiences"）+ 互联网视频（"billions of human action videos"）；后训练 = 遥操作（"the richest form"）+ 真实部署；2025 年营收从零到约 $30M | [K:series-c] |
| 2026-03-19 | ABB / UR / MiR / NVIDIA | 分阶段部署：先半结构化（工厂）→ 医院酒店 → 家庭；预训练用 Isaac Lab / Isaac Sim + Cosmos 合成增强；Foxconn Blackwell 线：取放汇流条、限位块、连拧 16 颗螺钉，端到端网络，"fine-tuned with a small amount of robot data (not necessarily even from a real robot)"，"In-context memory allows for long-horizon task execution" | [K:oem] |
| 2026-04-15 | 收购 Zebra 机器人部门（前 Fetch） | 仓储 AMR 平台 + Symmetry 编排软件并入 | [K:zebra] |
| 2026-08 | S1 发布 | 见 §2 | [K:s1] |
| 2026-09-10 | ARR $100M | 见 §3 | [K:arr] |

## 2. S1：上下文学习作为预训练的目的 [K:s1]

**论点**："Robotics thus far has been stuck in the BERT era"；引用自家 FACTR 2（Oh et al., 2026）：后训练数据足够密时，从零训练的策略能追平后训练的基础模型，于是"what is the point of pre-training?"——答案是 ICL。

**训练配方（只给到概念）**："pre-train on episodic data where the task is specified only through an in-context demonstration. Since the demonstration may come from a different scene, viewpoint, or embodiment, the policy must implicitly learn the demonstrator's intent, functional correspondences, and task progress"；"pre-training is the outer loop that teaches the policy how to learn from context"；无元学习机制说明；"future posts will go into depth on how S1 is trained"。

**接口**：输入 = 一段任务演示视频（可来自不同场景/视角/具身，示例为"One egocentric human video demonstration"）+ 当前观测；输出 = 机器人动作；"The same model weights produced every example shown in this blog"。频率、动作参数化、骨干、参数量均未披露。

**数据引擎三轴表**（一手原表）：

| 数据源 | 硬件接近度 | 多样性 | 可扩展性 |
|---|---|---|---|
| 机器人遥操作 | High | Low | Low |
| UMI | Moderate | Moderate | Moderate |
| 第一视角视频 | Low | High | High |
| 仿真 | Moderate | Low | High |

"Nothing wins on all three, which is why betting on a single source is short-sighted."

**ICL scaling（1k–100k h，ICL 与语言 VLA 同数据同架构同算力）**：seen 任务 1k h 时 VLA 53% > ICL 43%，扩到 100k h 后 ICL 96%；unseen 任务 VLA 9% vs ICL 66%。评测为内部两套基准，任务 4–8 分钟，"cumulative per-step success rate"，失败后人工干预继续。

**鲁棒性 L1–L5**：L2 物体随机移 15 cm/30°；L3 30 cm/45°；L4 换同可供性物体 + 约 15 cm 垂直位移；L5 摆放使半数动作必须换臂。L5 下 VLA 退化幅度是 ICL 的最高三倍；对提示与部署场景不一致，ICL 到 L4 仍稳，L5 才明显退化。

**演示效率**：单条上下文演示 ≈ 380 条后训练 episode；2,000 条后 VLA 86%。

**涌现**：扰动（推走物体、换物、改光照）下完成；错误重试（滑板轮装配）；常识替代（没有喷壶用杯子浇水；杯子快满就只加满）；**改正示范错误**（示范者摔了鸡蛋，S1 平稳完成）——"treats the demonstration as a specification of the goal, not a trajectory to reproduce"。

**时间线**：2025-09 LocoFormer → 2026-02 首次域内 ICL → 2026-05 首次翻煎饼 → 2026-08 S1 发布。盆栽任务从示范录制到自主执行 11 分钟。

## 3. 部署观：《The Hidden Pillar of Robotics》[K:arr]

- 60+ 付费客户，10 个月 ARR $100M，已确认收入 $50M；90% 操作、10% 移动。
- "a successful clip from a robot with 5%, 10%, or 99% accuracy can look exactly the same"；煎蛋一周做出第一个，两个月才在不同蛋与设置下可靠。
- "A robot that is 99.9% accurate but ten times too slow is not almost deployable. It's not deployable."
- 变化是常态（供应商换件、工位重排、装配顺序变）→ 每次都要采数据后训练不可扩展 → S1 的 ICL 由此成为优先级。
- 文化："If demos are what a company rewards, demos are what people will work on. We chose to reward deployment."
- Physical RSI：部署数据对专才增益小、对通才增益大；用"高中生分头读博再蒸馏回高中生"类比；"The more the generalist learns, the less specialization the next deployment should need."

## 4. 与 Dyna / Generalist / Sunday / Figure 的位置

- **动作真值**：Skild 预训练主体是仿真真值 + 互联网视频（无动作），后训练靠遥操作 + 部署 [K:series-c]，并自述在内部扩 UMI [K:s1]；四家里它是唯一四源都用的。
- **模型**：分层（高层低频 + 低层高频）[K:brain]，与 Figure 同派；但任务指定用视频而非语言 [K:s1]，与 Generalist 物理提示同派、与 Dyna "语言跟随进预训练" [research-four-routes §2.2] 相反。
- **飞轮**：Skild 认为部署数据"回到通才"才有价值 [K:arr]；Dyna 联创称部署未自加速（R-20）；两者不矛盾，都指向"回流的价值取决于是否进入基础模型"。
- **评测**：L1–L5 与"干预后累计逐步成功率"是本仓库 eval-protocol 缺的两个模板。

## 5. 对本仓库的启示与回写

1. **device 轨的外部佐证**：Skild 三轴表把 UMI 定位为唯一"三项均中"的来源并自述在扩 [K:s1]；device-track-umi.md §0 可引用为第三方（非 UMI 作者）验证。
2. **eval-protocol**：加 L1–L5 扰动阶梯作为泛化探针模板；真机协议模板加"干预记账"字段（干预次数、干预后是否继续计分），并要求报告"无干预成功率"与"累计逐步成功率"两口径 [K:s1]。
3. **策展预算比**：D-23 的 $1:$3 升为一手；program-plan §4 的复核基线不变，但可信度上调。
4. **演示库**：S1 与 GEN-1.5 都把"一段演示"当运行时输入；S1 进一步证明演示可来自不同视角/具身的人类第一视角视频 [K:s1]——human 轨片段可以直接成为提示，不必先转成机器人域。data-format-contract 的秒级切片导出（U-37 之外）应把 human 轨也纳入。
5. **诚实性**：S1 的 66%/9%/380 全部为内部基准与自报；训练方法未披露；D-23 更新为"一手核对，方法未披露"。

**回写清单**：governance D-23（本次改为一手）；research-dyna-comparison §4（指向本文）；eval-protocol §3（L1–L5、干预记账，待 M2）；device-track-umi §0（三轴表引用，待 M1 文档修订）。

## 6. 未披露项

S1 架构、参数量、控制频率、动作参数化；预训练数据小时数（只说"1k–100k h 子集"实验）；采集设备型号；仿真机器人 10 万具身的构成；质控的具体规则；客户名单之外的部署规模。
