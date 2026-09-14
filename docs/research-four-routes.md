# Figure / Dyna / Sunday / Generalist 四家技术路线精读（2026-09-14）

> **来源规则**：本文每条事实后面都带一手资料引用，指向仓库内归档的原文文本 [docs/sources/](sources/MANIFEST.md)（38 篇，2026-09-14 curl 直抓，每个文件头部有 URL、页面日期、原始 HTML sha256）。记法：`F:` = `sources/figure/`，`D:` = `sources/dyna/`，`S:` = `sources/sunday/`，`G:` = `sources/generalist/`，键与文件的对应见文首定义块；引用带英文原句片段时可直接在文件里 grep。**没有一手引用的句子只有两类**：标 ⚠️ 的第三方转述（给 URL）和标"判读"的本文推断。四家性能数字全部为公司自报，无独立复现；登记 governance D-25–D-27。Dyna 的 DYNA-2 模型与基础设施精读在 [research-dyna-comparison.md](research-dyna-comparison.md)，其引用的 dyna.co 页面同样已归档为 [D:dyna-2]、[D:infra]、[D:dyna-1]。

[F:helix]: sources/figure/helix.txt
[F:helix-logistics]: sources/figure/helix-logistics.txt
[F:rl-walking]: sources/figure/reinforcement-learning-walking.txt
[F:scaling-helix]: sources/figure/scaling-helix-logistics.txt
[F:battery]: sources/figure/f-03-battery-development.txt
[F:laundry]: sources/figure/helix-learns-to-fold-laundry.txt
[F:dishwasher]: sources/figure/helix-loads-the-dishwasher.txt
[F:go-big]: sources/figure/project-go-big.txt
[F:figure-03]: sources/figure/introducing-figure-03.txt
[F:bmw]: sources/figure/production-at-bmw.txt
[F:helix-02]: sources/figure/helix-02.txt
[F:living-room]: sources/figure/helix-02-living-room-tidy.txt
[F:ramping]: sources/figure/ramping-figure-03-production.txt
[F:bedroom]: sources/figure/helix-02-bedroom-tidy.txt
[F:f03-bmw]: sources/figure/f-03-at-bmw.txt
[F:index]: sources/figure/introducing-index.txt
[F:index-app]: sources/figure/index-app.txt
[F:nscale]: sources/figure/figure-and-nscale.txt
[D:dyna-1]: sources/dyna/dyna-1.txt
[D:dyna-1i]: sources/dyna/open-world-dexterity.txt
[D:pre-training]: sources/dyna/pre-training.txt
[D:dyna-2]: sources/dyna/dyna-2.txt
[D:infra]: sources/dyna/dyna-2-infrastructure.txt
[D:product]: sources/dyna/scaling-customer-deployments.txt
[S:act-1]: sources/sunday/no-robot-data.txt
[S:series-b]: sources/sunday/series-b.txt
[S:act-2]: sources/sunday/act-2-preview.txt
[S:technology]: sources/sunday/technology.txt
[G:preview]: sources/generalist/research-preview.txt
[G:lego]: sources/generalist/the-robots-build-now-too.txt
[G:gen-0]: sources/generalist/gen-0.txt
[G:commonsense]: sources/generalist/physical-commonsense.txt
[G:gtc]: sources/generalist/the-real-breakthrough-behind-our-gtc-demo.txt
[G:gen-1]: sources/generalist/gen-1.txt
[G:beyond]: sources/generalist/beyond-world-models.txt
[G:funding]: sources/generalist/accelerating-the-next-phase-of-physical-ai.txt
[G:hands]: sources/generalist/towards-machines-with-a-thousand-hands.txt
[G:gen-1.5]: sources/generalist/gen-1.5.txt

## 0. 一句话结论

四家在"人类是数据源"上已完全趋同，在**人类数据怎么变成动作真值**上分成三种做法，在**模型分不分层**上分成两派，在**评测标准**上正在从"成功率"转向"声明范围 + 适应成本"的可比口径：

| | Figure | Dyna | Sunday | Generalist |
|---|---|---|---|---|
| 本体 | 人形 Figure 03 [F:figure-03]；F04 设计已锁定 ⚠️（Adcock 2026-05，[Humanoids Daily](https://www.humanoidsdaily.com/news/figure-ai-reports-rapid-growth-for-index-surpassing-69-000-weekly-active-users)） | 固定双臂 6-DOF YAM + 平行夹爪 / WUJI-2 20-DOF 手 / 半人形原型 [D:dyna-2]；2027 上半年数百台 [D:product] | 轮式 + 伸缩脊柱 + 与手套同几何的手，"刻意非人形" [S:act-1]；77 kg、2.1 m ⚠️（[humanoid.guide](https://humanoid.guide/product/memo/)） | 不造本体；6/7/16+ DoF 半人形 [G:gen-0]；UR7e + MiR 几天内跑通 [G:gtc] |
| 预训练主语料 | Index 众包视频 16M 条、30 min/s [F:index]；Go-Big 人类第一视角视频 [F:go-big] | 100 万+ h 头戴人类视频，零机器人 [D:dyna-2] | 手套采的"传感化人类数据"，零遥操作 [S:act-1][S:act-2]；2,000+ 采集员 ⚠️（[Humanoids Daily](https://www.humanoidsdaily.com/news/sunday-unveils-memo-a-wheeled-domestic-robot-that-learns-from-200-gloves)） | 50 万+ h 手持夹爪人类数据，零机器人 [G:gen-1]、零仿真 [G:gen-1.5] |
| 动作真值 | 遥操作 [F:helix]；人类视频提取 head & hand tracks（Index 管线图，见 [research-figure.md](research-figure.md) §3.1） | 3D 手姿 → 腕位姿 + 拇食开合度 [D:dyna-2] | 手套硬件真值 + Skill Transform 抹人 [S:act-1] | 手持夹爪硬件真值（"pair of handheld grippers"）[G:gen-1.5] |
| 模型 | S2 7B VLM 7–9 Hz + S1 80M 200 Hz [F:helix] + S0 10M 1 kHz [F:helix-02] | Qwen3-VL-4B MoT VLA（DYNA-1）→ 视频扩散骨干 MoT + 流匹配 WAM（DYNA-2）[D:dyna-2] | ACT-1/ACT-2 单一端到端网络，架构未披露 [S:act-1][S:act-2] | GEN-0/1/1.5，99% 参数从零 [G:beyond]，Harmonic Reasoning 单流 [G:gen-0]，100 Hz [G:gen-1.5] |
| 分层 vs 统一 | 三层各自时标 [F:helix-02] | 四层栈 ⚠️（note.com 转述，见 dyna 报告 §1） | 导航 + 操作单模型 [S:act-1] | "不依赖 System1-System2 架构" [G:gen-0] |
| 新任务上线成本 | 8 h 精策划可用 [F:helix-logistics]；10→60 h 仍线性 [F:scaling-helix] | ≤10 h 后训练 [D:dyna-2]；1 h 微调 ~100% [D:pre-training] | 单条示例 SFT 教会可泛化折法；每户零适配 [S:act-2] | ~1 h → 99% [G:gen-1]；3–12 s 零梯度 59%，10 步 5 min 83% [G:gen-1.5] |
| 评测口径 | T_eff 对示范者归一化 [F:helix-logistics]；BMW 三 KPI [F:bmw] | "部署即评测"，每条生产 episode 按客户 SOP 打分 [D:product] | Solve = 性能 × 声明范围 × 适应成本 [S:act-2] | 盲测 A/B、MSE + 反向 KL [G:gen-0] |
| 数据基础设施亮点 | 10 Gbps mmWave 回坞卸数 [F:figure-03]；五阶段策展 [F:index]；视觉自标定 [F:helix-logistics] | MCAP + topic-group chunking [D:infra]；环形缓冲触发固化、SOP 自动标注、硬件退化指数 [D:product] | 48 小时迭代周期 [S:technology]；任务专属评分 + 多轮 QA [S:technology]；高质量子采样消融 [S:act-2] | O(10K) 核、专线上行、6.85 年经验/训练日 [G:gen-0]；任务向量定位数据缺口 [G:hands] |
| 开放度 | 无权重（各页无发布）；Index App 公开 [F:index-app] | 无权重（各页无发布） | Beta 家庭 2026 秋 [S:act-2] | "Early access partners will have access to GEN-1" [G:gen-1] |

对本仓库最重要的三条新结论：① **Sunday 给出了"泛化差距随预训练规模收敛"的可复用度量**（0% 预训练 82 点 → 100% 时 0 点）并证明高质量子采样在同数据量同算力下把 12.5% 数据的成功率从 43.8% 抬到 75.6% [S:act-2]；② **Dyna 把评测做成了数据基础设施**（SOP 分步自动标注 + 失败模式 + 硬件退化指数）[D:product]；③ **Figure 的学习式视觉自标定**是车队跨机迁移的关键工程件 [F:helix-logistics]。

---

## 1. Figure：人形本体 + 三层时标 + 众包视频

### 1.1 时间线（全部一手）

| 日期 | 里程碑 | 技术要点 | 来源 |
|---|---|---|---|
| 2025-02-20 | Helix | S2 = 7B 开源开放权重 VLM，7–9 Hz；S1 = 80M cross-attention encoder-decoder，200 Hz，35-DoF 上半身；约 500 h 多机多操作员遥操作（"<5%" 于既有 VLA 数据集）；事后反推指令自动标注（"What instruction would you have given the robot…"）；训练时给 S1/S2 输入加与部署延迟匹配的时间偏移；双嵌入式 GPU 各跑一系统；附加"任务完成百分比"合成动作维 | [F:helix] |
| 2025-02-26 | Helix Logistics | S1 隐式立体视觉（双相机特征在多尺度立体网络中合并后再分词，token 数不变）；**学习式视觉本体感知**："train a visual proprioception model to estimate the 6D poses of end effectors entirely from each robot's onboard visual input"，单机数据的策略跨多机部署；Sport Mode 动作块线性重采样到 0.8T、200 Hz 执行，最高 +50%；**8 h 精策划数据出可用策略**；策划后"⅓ less data" 吞吐 +40%；保留环境随机性导致的纠正、剔除操作员失误 | [F:helix-logistics] |
| 2025-03-25 | RL 行走 | 仿真 RL，数千并行本体各异参数，域随机化 + kHz 力矩闭环，零样本上 Figure 02 车队；奖励含人类步态参考轨迹 | [F:rl-walking] |
| 2025-06-07 | Scaling Helix | 10/20/40/60 h 消融：6.84 → 4.31 s/件（"58% increase in throughput"），条码 88.2% → 94.4%，"still in a low data regime"；新增视觉记忆、状态历史、力反馈入观测，decoder 头 +50% 参数后 4.05 s；人机交接靠"a few extra demonstration episodes" | [F:scaling-helix] |
| 2025-07-17 | F.03 电池 | 2.3 kWh、5 h 运行、2 kW 快充、成本比 F.02 降 78%、UN38.3 + UL2271 在认证 | [F:battery] |
| 2025-08-12 / 09-03 | 叠毛巾 / 装洗碗机 | "no modifications to the model or training hyperparameters. The only addition was the dataset"；无显式物体表征 | [F:laundry][F:dishwasher] |
| 2025-09-18 | Project Go-Big | Brookfield 10 万+ 住宅单元；"After training on 100% human video only, Helix has learned to navigate"，输出 SE(2) 速度命令，"No robot demonstrations whatsoever"；单一网络同时输出操作与导航 | [F:go-big] |
| 2025-10-09 | Figure 03 | 相机帧率 2×、延迟 1/4、视野 +60%；掌心相机；自研指尖触觉 3 g；**10 Gbps mmWave 回坞卸数**；2 kW 足底无线充电；BotQ 12,000 台/年，四年 10 万台；执行器 2× 速度 | [F:figure-03] |
| 2025-11-19 | BMW 收官 | Figure 02 11 个月，10 h 班次周一至周五，9 万+ 零件、1,250+ h、3 万+ 台 X3；KPI 三项：周期 84 s（装载 37 s）、放置 >99%/班、干预 0/班；5 mm 公差 2 s；前臂是最高故障点 → F03 腕部电子重构 | [F:bmw] |
| 2026-01-27 | Helix 02 | **S0 10M 参数 1 kHz** 全身控制器，"over 1,000 hours of joint‑level retargeted human motion data"、20 万并行环境仿真 RL，替换 109,504 行 C++；S1 "All sensors in. All actuators out"（头/掌相机 + 指尖触觉 + 全身本体感知 → 全身关节目标）；4 分钟 61 个动作洗碗机任务；药片、5 ml 注射器、金属件 | [F:helix-02] |
| 2026-03-09 / 05-08 | 客厅 / 卧室 | 双人形"single learned VLA policy… no shared planner… no message passing"，靠视觉读伙伴意图整理床铺；脚踩踏板、髋关抽屉 | [F:living-room][F:bedroom] |
| 2026-04-29 | 产能爬坡 | 350+ 台 F03，1 台/天 → 1 台/小时（<120 天 24×）；150+ 联网工位 MES；末端首检良率 >80%，电池线 99.3%，9,000+ 执行器 10+ SKU；每台 80+ 项测试 + 数千次全身 burn-in；FMS + OTA + 现场服务系统 + "fallback ladders"；**S0 接入感知**：头部 RGB 经立体模型提升为 3D 表征输入 S0，仿真 RL 零样本爬楼梯 | [F:ramping] |
| 2026-06-30 | F.03 到 BMW | 从钣金上料转到"sequencing"排序工位；Helix 02 边走边操作、拉带脚轮的重金属车 | [F:f03-bmw] |
| 2026-08-25 | Index | "Prior to this we tried buying data. Vendors couldn't hit the throughput, diversity, or quality bar"；五阶段管线（filtering / fraud review / deduplication / rebalancing / annotation），去重"discard those above a similarity threshold"，再平衡"task quotas… and embedding-based clusters"；"generalization results we're seeing internally… will be sharing more in detail on this soon" | [F:index] |
| 2026-09-03 | Nscale 算力 | 最多 10 万块 GPU（Vera Rubin），首期 $3.5B、意向 >$6B，2027 下半年起；"Figure is entering a phase where we are largely bound by data and compute"；Index 已到 35 min/s | [F:nscale] |

### 1.2 路线判读

1. **分层是为时标，不是为模块化**（判读）。三层分割线全是控制频率（7–9 Hz / 200 Hz / 1 kHz）[F:helix][F:helix-02]，且端到端联合优化："Gradients are backpropagated from S1 into S2 via the latent communication vector" [F:helix]。Generalist 反对的是"VLM 慢思考 + 单独动作头"的分层 [G:gen-0]，与 Figure 的时标分层不是同一件事。
2. **数据策略是三段式叠加**（判读）：遥操作对齐层 [F:helix][F:scaling-helix] + 人类视频预训练层 [F:go-big][F:index] + 仿真与动捕训 S0 [F:helix-02]。三段数据分别喂三层模型，这正是本仓库四轨设计的样板，只是 Figure 没有 device 轨。
3. **人类视频的直接迁移结果目前只公开了导航** [F:go-big]；操作层面"稍后分享" [F:index]。截至 2026-09-14，Index 对操作的价值是论点而非证据（判读）。
4. **工程护城河在车队闭环**（判读）：回坞卸数 [F:figure-03]、视觉自标定 [F:helix-logistics]、fallback ladders / FMS / OTA [F:ramping]。

### 1.3 未披露项（⚠️ 各页均无）

遥操作硬件方案；S2 具体骨干；相机数量与分辨率；存储格式与时间对齐方案；Index 头戴设备规格；人类视频到操作的迁移结果；Figure 04 规格。

---

## 2. Dyna：RM 自举 → 世界-动作模型 → 部署即评测

DYNA-2 的架构、100 万小时 scaling、消融与 MCAP 基础设施见 [research-dyna-comparison.md](research-dyna-comparison.md) §2（来源 [D:dyna-2][D:infra][D:dyna-1]），本节只补三篇未精读的一手页。

### 2.1 DYNA-1 系列两篇短文

- **DYNA-1i（2025-10-15）** [D:dyna-1i]：VLA "still suffer from performance degradation when deployed in environments not represented in the training data"；DYNA-1i "requiring only tens of hours of post-training data collected entirely in our office"；30 分钟连续叠衣：已见环境 22 件、未见（门厅/停车场/CoRL）20 件，均 ~40/hr；"Typically… requires collecting data across tens or even hundreds of unique environments"，靠"sophisticated modeling and data collection techniques"降低（未披露是什么）。
- **DYNA-1 预训练更新（2025-11-20）** [D:pre-training]：新 base "can perform diverse, dexterous tasks—including laundry folding and package sorting—without any post-training, even in environments it has never seen"；"reach roughly 100% success with as little as one hour of demonstration data"（叠杯、切芹菜、做早餐、铺桌垫）。

### 2.2 《Not Just a Model, But a Product》（2026-08-27）[D:product]

| 主题 | 一手内容（原句可 grep） | 对本仓库 |
|---|---|---|
| 商业里程碑 | 鼎泰丰 "rolling out Dyna's robots across its restaurant network"；酒店/物流/数据中心在推；"deployed fleet to hundreds of robots by the first half of 2027"；新站点"from setup to meeting production ROI bar, is as short as three days" | R-20 的另一面：飞轮不自加速，但基础设施可以让每次部署更快 |
| 产品指标 | 需求"1,500 table-ready napkins in an 18-hour shift"；DYNA-1 "about 480… roughly 35 napkins an hour, and only 75% cleared the quality bar"；DYNA-2 "95 napkins an hour, and 93% meet the quality bar… 1,590… a day" | 与研究页 46 → 87% [D:dyna-2] 是同一站点两种口径；登记 D-26 |
| 可操控性 | "Ten bin positions in one small bin is much harder: visually, each placement looks nearly identical"；"nearly every commercially viable task we've found requires some sort of instruction following"；解法进预训练而非按仓位训模型 | L3 子任务级指令要能表达空间槽位；eval-protocol 加"视觉相似目标的指令区分"探针 |
| 部署即评测 | "An hour of testing catches a model that doesn't work. It doesn't catch one that fails once every two hundred trials, degrades over a week, or runs fine on this robot and badly on the one beside it"；记录"camera streams, robot state, control commands, application events, and hardware telemetry, with enough timing information"；"over a terabyte of raw data every day" | eval-protocol §3 加"生产连续评测"档；data-platform 按 1 TB/站/天校核 |
| 录制器 | "continuously maintains a fixed-size, in-memory window of recent activity… promotes the relevant window to durable storage as a replayable episode, preserving the lead-up… Episodes land on local disk first; upload runs asynchronously… local copy is deleted only after the upstream copy is verified" | 与 capture-devices-design D5 触发式固化同构，第二家验证 |
| SOP 阶梯自动标注 | "segments each run into the steps of the task's SOP: which step… when it began and ended, whether it succeeded, and which failure mode applied"；人工只看"new tasks and label ontologies, rare or ambiguous outcomes, low-confidence outputs, suspected regressions, and a sampled slice"；标签让 episode 可按"site, robot, hardware state, and date"查询并回答"whether the current data mix has enough examples" | curation §3.2 + §4.1 合体，加失败模式本体与按标签查配比 |
| 案例 | 吞吐下滑 → Step 1 missed grabs 翻倍 → "It turned out to be a worn gripper… a worn gripper and a bad policy look the same in an episode" | robot 轨 EpisodeMeta 加 `hardware_health` |
| 硬件退化指数 | "robot state shows a joint that's drawing more current or tracking its commanded path less precisely… camera streams show the physical result"；对每台建基线，"flag a fault the same day it appears" | robot-track-teleop §6 / runtime §4 加退化指数 |
| 训练取用 | "The problem becomes curation rather than volume. Training on the right few hours can beat training on more of the wrong data"；"starting to shape what we pre-train on, not just what we post-train on" | CLAUDE.md 决策 6 的第三方佐证 |

### 2.3 路线判读

Dyna 是四家里唯一公开承认自测 99.4% [D:dyna-1] 与客户质检 46% [D:dyna-2] 之间鸿沟并用基础设施去填的公司（判读）。技术路线是三条并行：模型（RM 自举 [D:dyna-1] → WAM [D:dyna-2]）、数据（H5 → MCAP → 百万小时 [D:infra]）、评测（实验室 → 生产 [D:product]）。

---

## 3. Sunday：手套定义机器人 + 单模型 + Solve 标准

### 3.1 一手要点

**数据机制** [S:act-1][S:technology]
- 核心命题："to solve the data problem, we must solve the 'embodiment mismatch problem.' If we can align the robot's form factor with the human body, any data captured from humans can be directly translated" [S:act-1]。
- 手套与手"share the exact same geometry and sensor layout"；"If a human can do it in the glove, the robot can also do it" [S:act-1]。
- Skill Transform："aligns the raw observations—both kinematic and visual—to eliminate human-specific details… 90% success rate" [S:act-1]。
- 采集员 Memory Developers "collect from their lived-in homes, rather than warehouses"；"task-specific rating and multiple rounds of QA"；"48 Hour Cycle" [S:technology]。
- 第三方 ⚠️：2,000+ MDs、手套 $200–400、约 1,000 万条轨迹（[Humanoids Daily](https://www.humanoidsdaily.com/news/sunday-unveils-memo-a-wheeled-domestic-robot-that-learns-from-200-gloves)、[Sacra](https://sacra.com/c/sunday/)）。手套集成相机见 [research-sunday.md](research-sunday.md) §1 产品图。触觉/力是否记录未披露。

**ACT-1（2025-11-19）** [S:act-1]
- "solving ultra long-horizon tasks, generalizing room-scale mobile manipulation to new environments… all without a single trajectory of teleoperation data"。
- 地图条件导航："we condition it on 3D maps of its environment during training… when dropped into a new house, ACT-1 is able to utilize the given 3D map"；"the first foundation model that combines long-horizon manipulation with map-conditioned navigation in a single end-to-end model"。
- Table-to-Dishwasher："33 unique and 68 total dexterous interactions with 21 different objects while navigating more than 130 ft"；6 个 Airbnb 零样本；叠袜、浓缩咖啡（空中压粉、整机身力矩锁把手）。
- "from millimeter-level manipulation to meter-level room-scale navigation"。

**ACT-2 预览（2026-07-17）** [S:act-2]
- 泛化差距定义："the difference between in-domain and out-of-domain success after post-training"，每点 50 次评测：

| 预训练规模 | 域内 | 域外 | 差距 |
|---|---|---|---|
| 0% | 96% | 14% | 82 |
| 12% | 100% | 90% | 10 |
| 25% | 100% | 92% | 8 |
| 50% | 100% | 96% | 4 |
| 100% | 100% | 100% | 0 |

- 数据质量消融："At matched data volume and compute, higher-quality data produces lower validation loss and higher downstream success"：高质量子采样 12.5%/25%/50% → 75.6% / 87.9% / 92.3%；均匀子采样 → 43.8% / 53.6% / 64.1%；旗舰 99.1%，验证损失 0.0738 → 0.0653；"a practical signal for improving the data mixture before running expensive physical evaluations"。
- 单条示例："We post-trained four independent copies… Each copy received one demonstration of a different folding technique… All four models successfully executed their newly learned techniques" 于未见衣物。
- Solve："reliable performance across a declared scope, at a stated adaptation cost"；范围 = 9 类衣物 XXS–8XL、未见房间/床/光照、篮中/堆中/地上；适应成本 "Zero per home"；"785 autonomous attempts… 99.1% (±0.3% standard error)"，778 次成功；两轮独立标注、评分表事前固定；质量 4.72/5、98.3% ≥4 星；中位 2 min 13 s；衬衫最低 94.7%。
- 涌现：地上衣物回收、儿童干扰、对抗扰动；8XL 与婴儿衣靠移动底盘与脊柱扩展工作范围。
- 同一 base 在学"vacuuming, toy organization, fastening zippers, turning pants inside out, and coffee preparation"，未按 Solve 评测。
- Series B [S:series-b]：工程 3×、研究 4×、数据运营 5×；"fastest model iteration loop in robotics"；"We also benefit from improvements in public datasets, such as world models and VLMs"。

### 3.2 路线判读

1. Sunday 是"采集端定义本体"的极端案例（判读，依据 [S:act-1] 的 co-design 段落）。代价是任务集受夹爪限制；收益是手套数据 100% 有硬件真值且与本体零几何差。
2. 四家里唯一把策展价值量化的：高质量子采样在 12.5% 数据上比均匀多 32 个点 [S:act-2]。
3. Solve 标准对本仓库 eval-protocol 直接可用 [S:act-2]。
4. 未披露：模型架构、参数量、骨干、数据小时数、传感器套件、Skill Transform 方法。

---

## 4. Generalist：从零训练的单流模型 + 手持夹爪数据引擎

### 4.1 一手要点（10 篇博客，2025-06-17 至 2026-08-19）

**数据引擎**
- 研究预览 [G:preview]："end-to-end deep neural network mapping pixels and other sensor data to 100Hz actions"；跨具身 "7-DoF Flexiv Rizon 4, and 6-DoF UR5"，紧固件任务 "used no data from UR5 arms"。
- GEN-0 [G:gen-0]："over 270,000 hours… growing at a rate of 10,000 hours a week"；"1,000s of data collection devices and robots"；"laying new dedicated Internet lines"、"O(10K) cores"、"dozens of Petabytes"、"6.85 years of real-world manipulation experience per day of training"。
- 数据来自"multiple data foundry partners"，Class 1（"specific tasks"）/ Class 2 / Class 3（"do-anything"），8 种预训练集在 10 个长程任务集上对照，指标"validation prediction M.S.E." + "reverse Kullback–Leibler divergence"；"models with both low prediction errors and low reverse KL tend to perform better with supervised finetuning… high prediction errors and low reverse KL tend to be more distributionally multimodal, which can help post-training reinforcement learning" [G:gen-0]。
- 物理常识文 [G:commonsense]："teleoperation often breaks the sensorimotor loop: latency, limited tactile feedback, and unnatural interfaces push operators away from fast, reactive control"；"an object does not actually fall twice as fast"；手持设备"the force feedback is there—after a few minutes of doing a task, operators stop 'thinking' and start reacting"。
- 千手文 [G:hands]："approximately 9,000 variations so far"；ΔW = W_ft − W_0 按"sensor processing, harmonic reasoning, and actuation"分解，"range from 2.5% to 11.4% in relative parameter norm"；"Whisks… shift the sensor-processing weights far more than peelers… That points straight to a data intervention: collect more thin, visually sparse tools"；任务中途换末端"finds a new trajectory and contact strategy"。

**模型**
- GEN-0 [G:gen-0]：Harmonic Reasoning "asynchronous, continuous-time streams of sensing and acting tokens… without depending on System1-System2 architectures or inference-time guidance"；骨化相变 "1B models struggle… 6B models begin to benefit… 7B+ models are able to internalize"，已到 10B+；幂律 "L(D) = (D_c / D)^{α_D}"；真机 A/B "post-trained on only 5.6 hours of task-specific data"，最高 99% 需 "full pretraining dataset and all (550+ hours)"；预训练与后训练"collected by different people in entirely different environments"。
- GEN-1 [G:gen-1]："trained from scratch on our dataset of now half a million hours"；"The pretraining dataset contains no robot data"；"only approximately 1 hr of robot data"；三任务 99% vs GEN-0 64% vs 无预训练 19%；折箱 12.1 s vs ~34 s；含"learning from experience (RL), multimodal human guidance, as well as new inference-time techniques"、"inventing new forms of paged attention"；"more accurate to refer to GEN-1 as a system"；"not all tasks that we have attempted are able to hit these rates"；对齐一节承认涌现"can be… a liability"。
- 《Beyond World Models & VLAs》[G:beyond]："approximately 99% of the parameters are trained from scratch"；"if you have enough data and compute, training from scratch always wins"；VLM 预训练"can be a helpful crutch while we don't have enough robotics data"。
- GEN-1.5 [G:gen-1.5]："processes video input (30 seconds of memory, alongside other sensor, language, and proprioceptive inputs) and produces 100 Hz action trajectories"；"training continuously for over eight months"；物理提示 "3 to 12 seconds of a single demonstration, no training required"，10 任务 59%±10%；"10 gradient steps on 5 minutes of data per task (~50 demonstrations)" 83%±9%；1 步 1 min 66.5%；"Ten steps change the model weights… by less than 0.15%"；"no architectural changes to promote in-context learning, no inner or outer meta-learning loop… no auxiliary objectives"；"pretraining contains no simulation data" 但仿真 rollout 可作提示；"a person can demonstrate a task with their own hands, in view of the robot's cameras"；两条提示可拼接；香蕉当刷、簸箕铲块。

### 4.2 路线判读

1. "数据决定论"最纯形态（判读）：不造本体、不用仿真 [G:gen-1.5]、不用 VLM 骨干 [G:beyond]、不分层 [G:gen-0]。
2. 数据配比科学化到可运营：代工伙伴 × 三类数据 × MSE/反向 KL [G:gen-0] × 任务向量分解 [G:hands]。
3. 物理提示改变数据消费形态 [G:gen-1.5]：策展片段既是训练素材也是运行时输入。
4. 未披露：参数量、算力、设备照片与规格、代工伙伴身份、RL 方法、评测任务数与次数。

---

## 5. 横向对比

### 5.1 技术栈四层

![图 1：四家技术栈四层对照](assets/strategy/r03-four-stacks.svg)
*图 1　四家技术栈四层对照：本体 / 数据 / 模型 / 部署评测。色条表示该层的动作真值来源（蓝 = 机器人遥操作/车队，橙 = 人类视频伪动作，绿 = 人类手持或穿戴设备硬件真值，黄 = 仿真；本体行灰色）。数字出处同本文各节。*

### 5.2 模型接口：输入 / 输出（三家有一手细节，Figure 见 §1.1）

| | 输入 | 输出 | 动作空间 | 未披露 | 来源 |
|---|---|---|---|---|---|
| **Figure Helix 02** | S2：单目图像 + 机器人状态（腕位姿、指位）+ 语言 [F:helix]；S1：头相机 + 掌心相机 + 指尖触觉 + 全身本体感知 + S2 隐向量 [F:helix-02]，物流版加视觉记忆、状态历史、力反馈 [F:scaling-helix]；S0：全身关节状态 + 基座运动 + 头部立体 3D 表征 [F:helix-02][F:ramping] | S1 200 Hz 全身关节目标（含单指、躯干、头）+ 任务完成百分比 [F:helix][F:helix-02]；S0 1 kHz 执行器指令 [F:helix-02]；导航输出 SE(2) 速度 [F:go-big] | 初代 35-DoF 上半身 [F:helix]，Helix 02 全身 [F:helix-02] | 相机数、分辨率、动作块长 | 同左 |
| **Dyna DYNA-2** | 条件 c = "past frames, proprioception, and the language instruction"；本体感知 "tokenized and fed directly as input to the action transformer"；文本 "Video tokens cross-attend to text tokens; text does not directly influence action tokens"；多视角（蒸馏实验为 "three-second, three-view manipulation video"，鲁棒性实验 "Top cam covered"） | 动作块 a（流匹配去噪；评测按"action dimensions and the chunk horizon"归一化）；未来视频潜变量 z 只在训练时预测，推理"reactive"、不读预测视频 | 预训练伪动作 = "wrist poses for end-effector trajectories, and a continuous grasp signal derived from the thumb–index aperture"，且"do not perform any visual or embodiment-specific data processing"；后训练具身：6-DOF YAM + 平行夹爪、WUJI-2 20-DOF 手、半人形原型 | 控制频率、块长、相机数与分辨率、骨干来源、参数量 | [D:dyna-2] |
| **Dyna DYNA-1** | 图像 + 指令（Qwen3-VL-4B 初始化的 MoT 式 VLA [D:dyna-2]）；旁路奖励模型看观测"estimate task progress" [D:dyna-1]；生产版接受"typed instruction"指定堆位 [D:product] | 动作（形式未披露）；RM 输出任务进度 | 双臂 + 夹爪 | 动作参数化、频率 | [D:dyna-1][D:dyna-2][D:product] |
| **Sunday ACT-1/2** | 机器人相机（数量型号未说）；**环境 3D 地图**作条件 [S:act-1]；本体感知未明说；**语言指令全文未出现**；力是否输入未说（只写"force sensitivity of ACT-1 allows Memo to hold two wine glasses"） | Memo 整机动作："from millimeter-level manipulation to meter-level room-scale navigation" [S:act-1]，即底盘 + 脊柱 + 双臂 + 与手套同几何的手 | 训练数据侧 = 手套运动学 + 头戴/手套相机视频，经 Skill Transform 变成机器人域观测-动作对 [S:act-1] | 架构、参数量、频率、块长、骨干 | [S:act-1][S:act-2] |
| **Generalist GEN-1.5** | "video input (30 seconds of memory, alongside other sensor, language, and proprioceptive inputs)"；物理提示 = "sensorimotor examples (i.e. sensor data plus action trajectories)" 放进同一 30 s 上下文，其余为滚动观测；提示来源可为手持夹爪人类数据、机器人 rollout、仿真 rollout、人在机器人相机前的裸手示范 | "100 Hz action trajectories"；无独立动作头，感知流与动作流是 Harmonic Reasoning 的两条异步连续时间 token 流 [G:gen-0] | 跨具身（6/7/16+ DoF、~9,000 种末端 [G:hands]）；参数化未披露（判读：Data Hands 只记录夹爪位姿 + 开合，大概率是末端级动作） | 相机数、动作参数化、参数量 | [G:gen-1.5][G:gen-0][G:hands] |

### 5.3 分歧点

| 维度 | 分歧 | 谁在哪边 | 证据强度 |
|---|---|---|---|
| 动作真值来源 | 硬件记录 vs 视觉伪动作 | Generalist [G:gen-1.5]、Sunday [S:act-1] 硬件；Dyna 伪动作 [D:dyna-2]；Figure 遥操作 + 人类视频 [F:helix][F:index] | 各家只有自家曲线；Dyna 自认伪动作缺手指/力/触觉 [D:dyna-2] |
| 本体 | 人形 vs 非人形 | Figure "perspectives and kinematics mirror our own" [F:go-big]；Sunday 非人形 [S:act-1]；Dyna 固定双臂起步 [D:dyna-2]；Generalist 不选边 [G:hands] | Figure 的人形优势论目前只有导航迁移证据 [F:go-big] |
| 模型分层 | 时标分层 vs 单流 | Figure 三层 [F:helix-02]；Generalist 单流 [G:gen-0]；Sunday 单模型 [S:act-1] | 100 Hz 单流 [G:gen-1.5] 与 200 Hz S1 [F:helix] 都达商用速度，无法判优 |
| 骨干来源 | VLM 初始化 vs 从零 | Figure S2 开源 VLM [F:helix]，DYNA-1 Qwen3-VL-4B [D:dyna-2]；Generalist 99% 从零 [G:beyond]；DYNA-2 视频扩散骨干 [D:dyna-2] | "从零总是赢"只有自家数据 [G:beyond] |
| 训练目标 | 纯动作 vs 联合未来帧 | Dyna-2 联合 39/39 胜 [D:dyna-2]；Generalist "combining ideas from across… VLAs, world models, and beyond" [G:beyond] | 见 U-37 |
| 仿真角色 | 全身控制层 vs 不用 | Figure S0 全仿真 RL [F:helix-02]；Generalist 零仿真预训练但可作提示 [G:gen-1.5] | — |
| 部署形态 | 自有车队 vs 卖模型 | Figure [F:ramping]、Sunday [S:act-2]、Dyna [D:product] 自有；Generalist 早期访问 [G:gen-1] | — |

### 5.4 收敛点

1. **人类是主要数据源，机器人数据是对齐层**：每任务机器人数据 Figure 8–60 h [F:helix-logistics][F:scaling-helix]、Dyna ≤10 h / 1 h [D:dyna-2][D:pre-training]、Generalist 1 h → 5 min → 12 s [G:gen-1][G:gen-1.5]、Sunday 单条示例 [S:act-2]。
2. **质量 > 数量已被四家分别量化**：Figure "⅓ less data" +40% [F:helix-logistics]；Sunday +32 点 [S:act-2]；Generalist "data quality and diversity matters more than sheer volume" [G:gen-0]；Dyna "right few hours can beat… more of the wrong data" [D:product]。
3. **评测在向可比声明演进**：T_eff [F:helix-logistics]、Solve [S:act-2]、部署即评测 [D:product]、盲测 A/B [G:gen-0]。
4. **涌现即兴与恢复被三家独立观察**：Figure 拍平快递袋 [F:scaling-helix]、多抓退回 [F:laundry]；Generalist 香蕉当刷 [G:gen-1.5]；Sunday 地上衣物回收 [S:act-2]；Generalist 明说它也是对齐负债 [G:gen-1]。
5. **车队数据基础设施是共同补齐方向**：[F:figure-03][F:ramping]、[D:product][D:infra]、[S:technology]、[G:gen-0]。

### 5.5 与本仓库四轨的映射

| 本仓库轨 | Figure | Dyna | Sunday | Generalist |
|---|---|---|---|---|
| robot | 主对齐层 + 车队回流 [F:helix][F:ramping] | 后训练 + 生产回流 [D:dyna-2][D:product] | 实验室 hill-climb + Beta 车队 [S:act-2] | 每任务 ~1 h [G:gen-1] |
| human | Index 预训练主轴 [F:index] | 100 万 h 预训练主轴 [D:dyna-2] | — | — |
| device | — | — | 手套预训练主轴 [S:act-1] | Data Hands 预训练主轴 [G:gen-1.5] |
| sim | S0 全身 RL [F:helix-02]、S1 视觉骨干仿真预训练 [F:helix] | — | — | 仅作提示来源 [G:gen-1.5] |

没有一家同时用满四轨（判读）；本仓库四轨共 schema 让配比消融可以跨这四种路线做。 四家之外，Skild 自述四源都在扩（仿真 + 互联网视频预训练，遥操作 + 部署后训练，并在内部扩 UMI），是最接近「四轨全用」的厂商，见 [research-skild.md](research-skild.md) §2。

---

## 6. 对本仓库的启示与回写清单

1. **eval-protocol 加"泛化差距"指标与"Solve 声明"格式** [S:act-2]。
2. **curation 高质量子采样消融进验收钩子** [S:act-2]，也是 L3 估值排序器（D-14）的直接验证方式。
3. **L3 输出加失败模式本体** [D:product]，配比统计可按失败模式切片。
4. **D5 录制器设计升为"两家验证"** [D:product]；robot 轨 EpisodeMeta 加 `hardware_health`。
5. **robot 轨标定规范加"学习式视觉自标定"** [F:helix-logistics]。
6. **指令跟随的空间槽位探针** [D:product]。
7. **数据配比的离线指标加反向 KL** [G:gen-0]。
8. **任务向量分析作为"该多采什么"的工具** [G:hands]，登记 U-38。
9. **诚实性**：四家全部自报；Sunday 自评标注 [S:act-2]、Figure 内部泛化结果未公开 [F:index]、Generalist 评测任务数少 [G:gen-1][G:gen-1.5]、Dyna 单站点 [D:product]。登记 D-25–D-27。

**回写清单**：governance（D-25–D-27、U-38，已登记）；eval-protocol §1/§3、curation §4.1/§7、robot-track-teleop §1/§6 + data-format-contract（待 M2）；capture-devices-design D5 状态（已改）；research-figure / research-sunday / research-generalist-dora 各加一手补充节（已加）。

## 7. 来源

一手：本文顶部 38 个引用键，全部对应 [docs/sources/MANIFEST.md](sources/MANIFEST.md) 中的归档文件（含 URL、页面日期、抓取日期、原始 HTML sha256）。第三方（⚠️，仅补一手缺失项）：Humanoids Daily（Index 周活 69,943 / 35 min/s；Memo 手套价格与采集员数；F04 设计锁定）、humanoid.guide（Memo 重量与脊柱高度）、Sacra（手套价格另一口径）、note.com（Dyna 四层栈命名）。
