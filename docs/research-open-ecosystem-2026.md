# 开源生态全景：数据集、基准、开源模型骨架、训练框架与资源消耗（2026-10-13）

> 范围：**能拿到手的东西**——开放权重模型、开放数据集、开放基准与训练框架，以及它们的算力/显存/推理/存储账。闭源五家（Figure / Dyna / Sunday / Generalist / Skild）的模型配方见 [research-model-recipes.md](research-model-recipes.md)，各家预训练数据配方与 0→1 工程要件见 [research-vla-pretraining.md](research-vla-pretraining.md)（本文 §3/§5 只补它没有的条目，不重复），格式/工具生态选型见 [research-opensource.md](research-opensource.md)。
>
> 来源属性标注：**论文** = arXiv / 会议一手；**官方** = 官方仓库 README / 模型卡 / 数据卡；**第三方** = 媒体、博客、聚合表（含社区维护的 [awesome-embodied-data-pyramid](https://github.com/worldbench/awesome-embodied-data-pyramid)，下称"数据金字塔表"）；**自报 ⚠️** = 发布方自己给的、无独立核实的数字。同一数据集在不同来源的规模常不一致（统计口径：全集 vs 过滤子集、轨迹 vs 小时），表中并列给出并注明。**license 列只写本次（2026-10-13）在官方页面核到的；写"未核"的在引入前必须按 [cleaning-algo-selection.md](cleaning-algo-selection.md) 的 license 规则补核。**

## 0. 一句话结论

| 问题 | 结论 |
|---|---|
| 人形 robot 轨能直接导入的开源真机数据 | 只有两份够格：**Unitree UnifoLM-WBT**（G1 全身遥操作，~50 任务 × ~300 条，第三方称 Apache-2.0）与 **Humanoid Everyday**（G1/H1，10.3K 条，CC BY 4.0）；AgiBot World 2026（G2，13.6 TB）规模最大但 **CC BY-NC-SA**，只能进研究分支 |
| human 轨可用的第一视角视频 | 商用可用且最大的是 **Egocentric-10K**（1 万小时，Apache-2.0，工厂场景，无手部标注）；带手部位姿的是 **EgoDex**（829 h，AVP）；NVIDIA 用的 **EgoScale 20,854 h 未开放** |
| 基准该信哪个 | 2026-06 审计论文：LIBERO / CALVIN 可被 0.09B 无语言探针刷到 SOTA、显著性 <20%；**RoboCasa-GR1（人形）与 RoboTwin 2.0（双臂）**更可信（显著性 53% / 74%）；真机榜用 **RoboChallenge Table30**（π0.5 任务特化 43.7% SR）与 **RoboArena** |
| 开源模型骨架 | 四条谱系收敛：VLM + 流匹配动作专家（π0/π0.5、GR00T N1.x、SmolVLA、MolmoAct2、StarVLA-π）；VLM + 离散 token（OpenVLA、π0-FAST、RDT2-VQ）；VLM + L1 回归头（OpenVLA-OFT）；世界-动作模型（GE-Act 2.0、Cosmos 3、DreamZero）。**π0.6 没有官方开放权重** |
| 训练框架 | 单机微调：**LeRobot**（覆盖 act→pi05→groot 全谱）与 **openpi**（Apache-2.0，JAX 不支持多机）；多机预训练/多基准研究：**StarVLA**（MIT，Qwen3-VL/3.5 骨干 + 4 种动作头 + 12 个基准，DeepSpeed，8→256 A100 扩展效率 ~80%）；TRI **VLA Foundry**（FSDP2 + WebDataset 多机，license 未注明） |
| 算力量级 | 3B 级 VLA 预训练 ≈ **3e4 GPU 小时**（GR00T N1.7 模型卡：64 节点 × 4 GB200 × 120 h = 30,720 GPU·h）；单任务微调 **1e1–1e2 GPU 小时**（π0.5 全参 4×H100 30k 步 ≈ 4.4 h；SmolVLA 4×H100 5k 步 28 min）；边缘推理 **π0 在 Jetson Thor 19 Hz、H100 162 Hz**（VLA-Perf） |

---

## 1. 开源数据集

### 1.1 真机数据（→ robot 轨）

| 数据集 | 发布 | 规模 | 具身 | 格式 | license | 来源属性 |
|---|---|---|---|---|---|---|
| [Open X-Embodiment](https://arxiv.org/abs/2310.08864) | 2023-10 | 22 种机器人、527 技能、160,266 任务、21 机构；轨迹数论文称 1M+，数据金字塔表记 2.4M（口径不同） | 多种单臂为主 | RLDS/TFRecord | 按子数据集各异，未核 | 论文 |
| [DROID](https://arxiv.org/abs/2403.12945) | 2024-03 | 76k 轨迹 / 350 h / 564 场景 / 86 任务 / 13 机构 | Franka | RLDS；LeRobot 版在 HF | 未核 | 论文；[DROID-3D](https://github.com/worldbench/awesome-embodied-data-pyramid)（2026，70K+ 条加深度，需申请） |
| BridgeData V2 | 2023 | 60.1K 轨迹 | WidowX | RLDS | 未核 | 数据金字塔表 |
| RH20T | 2023 | 110K 轨迹；140+ 任务 / 42 技能 / ~1,100 h | 多臂 | 自定义 | 未核 | 第三方综述 |
| [RoboMIND](https://arxiv.org/abs/2412.13877) / [RoboMIND 2.0](https://arxiv.org/abs/2512.24653) | 2024-12 / 2025-12 | 107K → 310K 双臂轨迹（290K 台面双臂 + 20K 移动双臂）、129 技能；"700+ 任务"为自报 ⚠️ | 多具身双臂 | HDF5/LeRobot | 原版第三方称 Apache-2.0，2.0 未核；HF 需登录 | 论文 |
| [AgiBot World Beta](https://arxiv.org/pdf/2606.17846) | 2025 | 1M 轨迹（金字塔表）；Qwen 报告实际用到夹爪子集 ~200 任务 / ~2,400 h | AgiBot G1 | LeRobot | **CC BY-NC-SA 4.0** | 论文 / 第三方 |
| [AgiBot World 2026](https://huggingface.co/datasets/agibot-world/AgiBotWorld2026) | 2026-03（快照 20260315） | 13.6 TB；分五期发布，第一期面向模仿学习；episode 数：金字塔表 20.7K、第三方指南 11,430 条 / 14 任务（互相矛盾，官方卡未给总数） | AgiBot G2（9 路相机含鱼眼/深度、触觉、LiDAR、IMU、全身关节） | LeRobot v2.1 | **CC BY-NC-SA 4.0**（官方卡） | 官方 |
| [Galaxea Open-World](https://arxiv.org/abs/2509.00576) | 2025-09 | ~100k 轨迹 / ~500 h / 150 任务 / 50 场景（综述）；金字塔表记 20.5K | Galaxea R1 | LeRobot | 第三方称 CC BY-NC-SA 4.0 | 论文 |
| RoboCOIN | 2025 | 180K 轨迹 | 多具身 | — | 未核 | 数据金字塔表 |
| [Humanoid Everyday](https://arxiv.org/abs/2510.08807) | 2025-10（v3 2026-07） | 10.3K 轨迹 / 3M+ 帧 / 260 任务 / 7 类 | **Unitree G1 + Dex3-1（带触觉）、H1 + Inspire**；AVP 遥操作上半身；RGB-D + Livox LiDAR | — | **CC BY 4.0** | 论文 |
| [Unitree UnifoLM-WBT](https://huggingface.co/collections/unitreerobotics/unifolm-wbt-dataset) | 2026-03-05 | ~50 个任务数据集，多数 300 条/任务（洗衣机放衣、晾衣、铺床、洗碗机、超市理货、推轮椅……），Brainco / Inspire / Dex1 三种手 | **Unitree G1 全身遥操作（上肢操作 + 下肢移动同录）** | LeRobot | 第三方（澎湃）称 Apache-2.0，HF 集合页未显示，**引入前核卡** | 官方集合 + 第三方 |
| [MolmoAct2-BimanualYAM](https://arxiv.org/abs/2605.02881) | 2026-05 | **720 h** 双臂遥操作、34.5K 轨迹、28 任务、146K 标注（自称最大开放双臂集） | YAM 双臂 | LeRobot | 未核（第三方称 Apache-2.0） | 论文 |
| [BEHAVIOR Challenge 2026 演示集](https://behavior.stanford.edu/challenge) | 2026-07 | **20,000 条 / 1,950 h**，100 个全长家务任务、7 场景，JoyLo 全身遥操作（底盘 + 躯干 + 双臂）；RGB-D + 本体 + 技能/子任务标注 | 仿真移动双臂 | — | 未核 | 官方 |
| PrimeBot Household | 2026 | 531.7 h / 32,518 条采集，500+ h 已放 | — | — | 未核 | 数据金字塔表 |
| OpenNeoData | 2026 | 200K+ 轨迹 / 5,000+ h | — | — | 未核 | 数据金字塔表（唯一来源） |
| 2026 其他 | 2026 | RoboInter-Data 230K+ 条 / 571 场景；LET-Base（乐聚）92.6K；ABC-130K 130.7K；EgoSteer-RealWorld 54K 条 / 192 h；Open-H-Embodiment 125.8K（医疗，CC BY 4.0，域外） | — | — | 未核 | 数据金字塔表 |
| [LeRobot Hub 社区数据](https://www.techtimes.com/articles/317129/20260525/open-source-robotics-ai-reaches-inflection-point-lerobot-hub-surpasses-58000-datasets-in-one-year.htm) | 持续 | **58,000+** 个 lerobot 标签数据集（2026-05，IEEE Spectrum 转述），2024 底为 1,145；无总小时统计；SmolVLA 用了其中 481 个 / 22.9K 条 | SO-100/101 为主 | LeRobot v2/v3 | 各异 | 第三方 |

### 1.2 人类第一视角视频（→ human 轨）

| 数据集 | 发布 | 规模 | 标注 | license | 来源属性 |
|---|---|---|---|---|---|
| Ego4D | 2021– | 3,670 h 日常生活 | 无原生手部位姿 | CC BY-NC | 第三方汇总（与论文一致） |
| Ego-Exo4D | 2023（IJCV 2025） | 1,286 h（期刊版；预印本 1,422 h）；740 人 / 13 城 / 123 场景 | 多视角 + 注视 + 点云 + 相机位姿 + IMU + 语言 | Ego-Exo4D 协议；[Ego-Exo4D-HM](https://github.com/worldbench/awesome-embodied-data-pyramid)（2026，2,649 takes / 104.6 动作小时）网格标注 CC BY 4.0 | 期刊 |
| [EgoDex](https://www.iclr.cc/virtual/2026/poster/10010617)（Apple） | ICLR 2026 | **829 h**，Apple Vision Pro 录制，**同步 3D 手/指追踪** | 原生手部位姿 | 未核 | 论文 |
| [Egocentric-10K](https://huggingface.co/datasets/builddotai/Egocentric-10K)（Build AI） | 2025-11 | **10,000 h / 2,153 名工人 / 1.08B 帧 / 16.4 TB**，全部真实工厂，无音频；WebDataset；gated（需填联系方式） | 无逐帧手部标注；配套 Egocentric-10K-Evaluation 1 万帧有手数 + 是否操作二值标签 | **Apache-2.0**（官方卡） | 官方卡 + [第三方](https://www.humanoidsdaily.com/news/build-ai-open-sources-10-000-hours-of-factory-worker-video-to-scale-robot-learning) |
| Egocentric-100K / Egocentric-1M（Build AI） | 2025-12 / 2026-04-08 | 100,000 h / 14,228 名东南亚工厂工人；"~100 万小时" | — | 称 Apache-2.0 | **单一第三方博客，未核 ⚠️** |
| [EgoScale](https://arxiv.org/abs/2602.16710)（NVIDIA） | 2026-02 | **20,854 h** 动作标注第一视角视频：9,869 场景 / 6,015 任务 / 43,237 物体，含 EgoDex 829 h；手部位姿与相机运动来自现成 SLAM + 手部估计管线（作者承认噪声大） | 伪动作标签 | **未见数据集开放**；是 GR00T N1.7 预训练数据 | 论文 |
| 2026 其他 | 2026 | EgoSuite-Open100K（标题称 10 万小时）、RekaDaily-10k（1 万+ h）、EgoWild 538.9 h（待放） | — | 未核 | 数据金字塔表 |
| 对照（闭源） | — | Dyna-2 100 万 h、Figure Go-Big、Generalist 50 万 h 无机器人数据：见 [research-dyna-comparison.md](research-dyna-comparison.md)、[research-figure.md](research-figure.md)、governance D-24 | — | — | — |

EgoScale 给了人类视频 scaling 的第一条公开曲线：人类数据规模与验证损失**对数线性**，验证损失与真机成功率强相关，两阶段（大规模人类预训练 → 50 h 对齐人类数据 + 4 h 机器人数据中训练）在 22-DoF 灵巧手上比无预训练提升 54%（论文）。这与 Dyna-2 自报的曲线（D-22）方向一致，是第二家独立证据。

### 1.3 手持 / 穿戴采集器数据（→ device 轨）

| 数据集 | 发布 | 规模 | 设备 | 来源属性 |
|---|---|---|---|---|
| UMI | 2024 | 2,543 轨迹 | UMI 手持夹爪 | 数据金字塔表 |
| FastUMI / FastUMI-100K | 2024 / 2025 | 8,965 / 100K 轨迹 | FastUMI | 数据金字塔表 |
| DexWild / DexUMI / exUMI / MV-UMI | 2025 | 9,505 / 1,792 / 1,660 / 1,370 轨迹 | 手套/灵巧 UMI 变体 | 数据金字塔表 |
| RealOmni-Open | 2026 | **13,000+ h / 5M+ clip**（2026-07-24 快照） | — | 数据金字塔表（唯一来源，未核） |
| Daimon-Infinity | 2026 | 274,669 轨迹 | — | 数据金字塔表 |
| [RDT2 的 UMI 数据](https://raw.githubusercontent.com/thu-ml/RDT2/main/README.md) | 2025-09 | **10,000+ h / 100+ 室内场景**，重设计 UMI | UMI | 官方 README；**只放模型，数据未见开放** |

device 轨的公开数据量级（1e2–1e4 h）已经和真机数据同档，但最大的两份（RDT2 UMI、RealOmni）都不开放或来源单一；我们 device 轨（[device-track-umi.md](device-track-umi.md)）的价值仍在自采。

### 1.4 仿真 / 合成（→ sim 轨）

| 数据集 | 发布 | 规模 | 来源属性 |
|---|---|---|---|
| [InternData-A1](https://arxiv.org/abs/2511.16651)（上海 AI Lab） | 2025-11 | **630k 轨迹 / 7,433 h / 4 具身 / 18 技能 / 70 任务 / 227 场景**；纯合成预训练的模型在 49 仿真 + 5 真机任务上追平官方 π0 | 论文；数据已放、生成管线"将开源" |
| [RoboCasa365](https://arxiv.org/abs/2603.04356) | ICLR 2026 | 365 任务 / 2,500 厨房 / **600+ h 人类演示 + 1,600+ h 合成演示** | 论文 |
| GR00T-X-Embodiment-Sim / DexMimicGen / DreamGen | 2025 | 见 [research-opensource.md](research-opensource.md) §6（88 h 真机 + 780K 合成） | 论文 |
| Dex1B / SynGrasp-1B | 2025 | 十亿级抓取演示 | 数据金字塔表 |
| AXIS / MATE | 2026 | 50,129 条 / 207 任务；2,500 条 / 24.1 h | 数据金字塔表 |

### 1.5 横向规律

1. **人形真机开放数据极少**：全表里具身是人形且开放的只有 Humanoid Everyday、UnifoLM-WBT、AgiBot World 系（G1/G2 为轮式人形），加起来 <1e4 条；其余 1e5–1e6 级都是单臂/双臂台面。这印证 [data-strategy-roadmap.md](data-strategy-roadmap.md) 的判断：人形数据飞轮只能自建。
2. **license 分裂**：中国厂商大集（AgiBot、Galaxea、InternVLA-A1）清一色 **CC BY-NC-SA**；美方（Ai2、Build AI、Unitree 数据、Humanoid Everyday）多为 Apache / CC BY。按 [CLAUDE.md](../CLAUDE.md) 规则，NC 数据只进研究分支，不进默认训练配方。
3. **统计口径不统一是常态**：同一数据集轨迹数差 5×（AgiBot 2026、Galaxea、OXE）。我们 lineage 表应同时记 episode 数、帧数、小时数与"过滤子集 of 全集"关系，避免复制这种混乱。
4. **人类视频比机器人数据大 1–2 个数量级且更便宜**，但开放的大集都缺手部标注（Egocentric-10K）或不开放（EgoScale）。human 轨伪标签管线（SLAM + 手部估计）是必建件，而且要像 EgoScale 一样如实记录噪声。

---

## 2. 基准

### 2.1 仿真基准

| 基准 | 具身 | 规模 | 2026 状态 | 来源属性 |
|---|---|---|---|---|
| LIBERO | Franka 单臂 | 130 任务 / 4 套件（Spatial / Object / Goal / Long） | SOTA ≥97%（OpenVLA-OFT 97.1%、ZR-0 97.8%）；**审计失败**：0.09B 无语言探针可达 SOTA，仅 19.8% 的 SOTA 声明统计显著 | 论文 |
| [LIBERO-Plus](https://www.sourcepulse.org/projects/26294051) | Franka | 10,030 测试实例，7 类扰动（布局 / 视角 / 初始状态 / 语言 / 光照 / 纹理 / 噪声） | 微调后 ~79.6%，视角与初始状态扰动掉分最重 | 第三方汇总 |
| CALVIN | Franka | 长时程语言条件 | **审计失败**：训练范围内随机化方块位姿即令所有策略掉分 | 论文 |
| SimplerEnv | WidowX / Google Robot | real-to-sim | 仅 19.7% SOTA 声明显著；StarVLA 最佳 WidowX 65.3 / Google 76.0 | 论文 |
| RoboCasa-GR1 Tabletop | **Fourier GR-1 人形** | 24 任务 | 显著性 53.3%；StarVLA 专家 48.8、通用模型 57.3 → **人形相关的首选仿真基准** | 论文 |
| [RoboCasa365](https://arxiv.org/abs/2603.04356) | 移动操作 | 365 任务 / 2,500 厨房 / 60 活动，原子 + 组合、seen + unseen | 榜首 RLDX-1 总分 33.2%，组合-unseen 最高仅 5.4% | 论文 |
| RoboTwin 2.0 | 双臂 | 强域随机化 | 显著性 73.7%；StarVLA ~88（clean / randomized 相近） | 论文 |
| [BEHAVIOR-1K](https://arxiv.org/abs/2403.09227) / [2026 Challenge](https://behavior.stanford.edu/challenge) | 移动双臂（OmniGibson） | 1,000 活动 / 50 场景；2026 赛：100 全长任务、7 场景、1,950 h 演示；指标 = BDDL 部分得分的平均任务成功 | 2026-07-02 启动，2026-10-16 截止，CoRL 2026 公布；2025 赛亚军方案基于 π0.5 | 官方 |
| EBench | 移动操作 | "元素级诊断"通用策略 | Qwen-RobotManip 报告用到；细节未核 | 论文提及 |
| RLBench / ManiSkill3 / Meta-World / Isaac Lab-Arena | 单臂 / 多 | — | StarVLA 集成 RLBench；Arena 为我们自建任务集所在（[eval-protocol.md](eval-protocol.md) §2） | — |

**审计论文**（[arXiv:2606.04233](https://arxiv.org/abs/2606.04233)，2026-06，TTIC）定义四类失效：捷径可解、无统计显著性、渐进过拟合、数据源依赖，并发布可复用的诊断实现（[ripl.github.io/manipulation_benchmark_audit](https://ripl.github.io/manipulation_benchmark_audit/)）。其"数据接近性"结论——小模型用更接近测试分布的演示训练可追平大模型——与我们"质量优先于吞吐"的决策 6 同向。

### 2.2 真机基准

| 基准 | 机构 | 形态 | 结果 | 来源属性 |
|---|---|---|---|---|
| [RoboChallenge Table30](https://arxiv.org/html/2510.17950v1) | Dexmal + Hugging Face | 10 台在线真机（UR5 / Franka / Cobot Magic Aloha / ARX-5），30 台面任务，每任务 10 次，成功率 + 进度分（满 100）；用户本地跑模型远程控机 | 论文版：π0.5 任务特化 43.7% SR / 62.2 分，π0 28.3，CogACT 11.7，多任务版 π0.5 17.7；2026-01 年报：榜首 ~50–60%（两份来源不一致），精细操作 <15%；Qwen-RobotManip 自报第一、相对 +20% ⚠️ | 论文 + 第三方 |
| [RoboArena](https://arxiv.org/abs/2506.18123) | UC Berkeley / Stanford 等 7 校 | 分布式众包：评测者自选任务与环境，盲测成对比较 → 偏好排名；DROID/Franka 平台，原型 600+ 对局 / 7 策略 | 比集中式评测排名更准（论文）；榜单对低样本模型加标；Cosmos 3 自称 RoboArena 第一 ⚠️ | 论文 |
| PhAIL | — | 真机 VLA 基准 + 分布式方法学；同一演示集微调 π0.5 / GR00T N1.6 / ACT / SmolVLA | 指出 π0.5 与 GR00T 学相对/增量动作，ACT 与 SmolVLA 学绝对笛卡尔目标，比较时需对齐动作表征 | 论文（[arXiv:2605.29710](https://arxiv.org/pdf/2605.29710)） |

### 2.3 评测工具

- [allenai/vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)：一套框架评任意 VLA 于任意仿真基准（含 VLABench）。
- StarVLA 内置 12 个基准（§4）。
- 对 [eval-protocol.md](eval-protocol.md) §2 的直接影响：LIBERO 保留为"社区可比"但**降为参考项**，每 checkpoint 回归主指标改为 **RoboCasa-GR1 + LIBERO-Plus 扰动集 + RoboTwin 2.0 子集**；真机引入 RoboArena 式盲测成对比较（我们 eval-protocol §3 已有盲测 A/B，可直接对齐）。

---

## 3. 开源模型骨架架构

只列**有开放权重**或明确开放代码的；参数量、骨干、动作头按官方页面。闭源的 Helix / DYNA-2 / ACT-1 / GEN / Skild Brain 见 [research-model-recipes.md](research-model-recipes.md)。

### 3.1 VLA（视觉-语言-动作）

| 模型 | 机构 / 日期 | 参数 | VLM 骨干 | 动作头 / 表征 | 预训练数据 | 权重 license | 来源属性 |
|---|---|---|---|---|---|---|---|
| OpenVLA | Stanford 等 / 2024-06 | 7B | Prismatic：DINOv2 + SigLIP 双视觉 + Llama-2 7B | 256-bin 离散 token，逐维自回归 | OXE 970k 轨迹 | 未核（代码仓库开放） | 论文 |
| [OpenVLA-OFT](https://openvla-oft.github.io/) | Stanford / 2025-02 | 7B | 同上 | **并行解码 + 动作分块 + 连续 L1 回归 MLP 头**；LoRA 微调，冻结视觉塔 | 基于 OpenVLA 微调 | 未注明 | 官方页 |
| π0 / π0-FAST | Physical Intelligence / 2025-02 | 2.7B（SigLIP-So 0.4B + Gemma-2B + 0.3B 动作专家；VLA-Perf 拆分）；论文口径 3.3B | PaliGemma | 流匹配动作专家 H=50 / FAST 离散 token | 10k+ h 机器人数据 | **Apache-2.0**（openpi LICENSE 核） | 官方 |
| π0.5 | PI / 2025-09（openpi） | ~3B（PaliGemma 2B + ~300M 专家） | PaliGemma | 流匹配（openpi 仅放流匹配头）；`pi05_droid` 带知识隔离 | 见 [research-vla-pretraining.md](research-vla-pretraining.md) §1.2 | Apache-2.0 | 官方 |
| π0.6 / π*0.6 | PI / 2025-11 | — | — | RECAP（演示 → 纠错 → RL） | — | **无官方开放权重**；只有社区复现（exla-ai/openpie-0.6、qrafty-ai/pi-openpi 等，Gemma-3 4B 变体），来源不可信 | 第三方 |
| GR00T N1 / N1.5 | NVIDIA / 2025-03 / 05 | 2.2B | Eagle-2 | 流匹配 DiT（N1.5 DiT 16 层 + 4 层适配器）H=16 | 见 research-vla-pretraining §1.3 | NVIDIA Open Model License | 论文 |
| GR00T N1.6 | NVIDIA / 2025 下半年 | 3B | 内部 Cosmos-Reason-2B 变体（Eagle 系），原生宽高比 | **DiT 32 层**，去掉 N1.5 的适配器；预训练解冻 VLM 顶 4 层 | 第三方博客：300k 步、全局 batch 16,384（未核 ⚠️） | 同上 | 官方 README + 第三方 |
| [GR00T N1.7](https://huggingface.co/nvidia/GR00T-N1.7-3B) | NVIDIA / 2026-04-17 GA | 3B | **Cosmos-Reason2-2B（Qwen3-VL 架构）** | 流匹配 DiT **16 层**（从 32 减回）；状态/动作维 29→**132**；H 16→**40**；每具身一组动作编解码器 | **20K h EgoScale 人类视频** + 多具身机器人演示；HF/NVIDIA 口径 ~32K h 真实演示 + 人类视频、~8K h 仿真（BEHAVIOR / RoboCasa / Sim GR-1）；模型卡：21.6M 数据点 / 13 数据集 | 代码 Apache-2.0，**权重 NVIDIA Open Model License**（README "fully commercially licensable under Apache 2.0"与许可节自相矛盾，已在 roadmap §1.8 登记） | 官方 |
| SmolVLA | Hugging Face / 2025-06 | 0.45B | SmolVLM-2（SigLIP 400M + SmolLM2 135M） | 流匹配专家 | 481 社区数据集 / 22.9K 条 | Apache-2.0 | 论文 |
| RDT-1B | 清华 TSAIL / 2024-10 | 1.2B | SigLIP + T5 | 扩散 DiT，128 维物理槽位 | 46 数据集 21 TB | 未核 | 论文 |
| [RDT2](https://raw.githubusercontent.com/thu-ml/RDT2/main/README.md) | 清华 / 2025-09（论文 2026-02） | 7B（VQ 版） | **Qwen2.5-VL-7B-Instruct** | RDT2-VQ：RVQ 离散 token 自回归；RDT2-FM：流匹配动作专家（低延迟） | 10k+ h UMI / 100+ 场景 | README 中 Apache-2.0 徽章被注释掉，**license 未明示 ⚠️**；基座 Qwen2.5-VL-7B 为 Apache-2.0 | 官方 |
| Wall-OSS-0.5 | 自变量 / 2026-05 | 4B | — | RVQ 离散 + 流匹配双通路 | 见 research-vla-pretraining §1.8 | 未核 | 论文 |
| [InternVLA-A1](https://arxiv.org/abs/2601.02456) | 上海 AI Lab / 2026-01 | 2B / 3B | InternVL3 / Qwen3-VL | **Mixture-of-Transformers**：理解 + 视觉预见 + 动作三合一 | InternData-A1 + AgiBot World，533M 帧；A1.5 称 1.2M 机器人 episode + 3M 多模态样本 | **CC BY-NC-SA 4.0**（模型卡） | 论文 + 官方卡 |
| [MolmoAct2](https://arxiv.org/abs/2605.02881) | Ai2 / 2026-05-04 | 未披露 | MolmoER（空间/具身推理专用 VLM，3.3M 样本 specialize-then-rehearse） | 离散 token VLM + **流匹配专家，逐层 KV 条件**；OpenFAST 开放 tokenizer（五具身百万轨迹）；Think 变体只重预测变化区域深度 token | 720 h 双臂 + DROID / SO-100 过滤子集 | **权重 + 代码 + 全部训练数据开放**；license 第三方称 Apache-2.0，未核 | 论文 |
| [Qwen-RobotManip](https://arxiv.org/pdf/2606.17846) | 阿里 Qwen / 2026-06-16 | 第三方称 Qwen3.5-4B | Qwen-VL 系 | 未披露 | **38,100 h 全开源数据 + 人类视频**，人→机管线转 15 平台 | **权重是否开放矛盾**（一处称有 GitHub 仓库、一处称"专有，发布时未放权重"）⚠️ | 论文 + 第三方 |
| MiniCPM-RobotManip | OpenBMB / 2026 | 1.5B | MiniCPM | — | — | **Apache-2.0**（HF） | 官方卡 |
| UnifoLM-VLA-0 | Unitree / 2026-01 | 7B 级 | Qwen2.5-VL-7B | — | — | 第三方转述 | 第三方 |
| StarVLA 系（VLAct、ABot-M0 权重） | 多机构 / 2026-04 | 4B 级 | Qwen3-VL-4B、Qwen3.5 0.8–9B、Florence-2、Cosmos-Predict2-2B、Wan2.2 | 四种可换头：FAST / OFT / π 流匹配 / GR00T 双系统 | 按基准训练 | **MIT** | 官方仓库 |
| ACT / Diffusion Policy（基线） | 2023 | ~80M / ~100M 级 | ResNet | Transformer 回归分块 / 扩散 | 单任务 50–200 条 | MIT（LeRobot 实现 Apache-2.0） | 官方文档 |

### 3.2 世界-动作模型（WAM）与世界模型

| 模型 | 机构 / 日期 | 规模 | 结构 | 数据 / 算力 | 开放状态 | 来源属性 |
|---|---|---|---|---|---|---|
| [GE-Act 2.0](https://arxiv.org/abs/2609.05588) | AgiBot / 2026-09-04 | 未披露 | **控制导向自编码器（CoAE）+ 单步视觉规划器（SVP）+ 逆动力学模型（IDM）**，全部从操作数据从零初始化 | 联合训练 300 → **30,000 h**；目标具身 G2-90D 仅占 <2% 仍 +17.7 pt；技能覆盖度与零样本 OOD 成功率 r=0.80 | 代码/权重未在摘要确认；Genie Envisioner v1.0 权重在 HF | 论文 |
| Cosmos 3 | NVIDIA / 2026-06-01 | Super = 32B 推理器 + 32B 生成器（64B 总）；Nano 8B（另一来源 16B，矛盾） | Mixture-of-Transformers（非 MoE），推理 + 世界生成 + 动作三模态，256K 上下文，10+ 具身动作域 | 20T 多模态 token；GPU 小时未披露 | 权重 **OpenMDW-1.1**（gated，需"Built on NVIDIA Cosmos"署名；roadmap §1.8 已登记） | 第三方（NVIDIA 技术报告待读） |
| DreamZero | NVIDIA / 2026-03 | — | 联合预测动作 + 视频的 WAM，DiT 缓存推理 | DROID 模型版已放 | 代码 + DROID 权重；第三方称 GR00T N2 基础 ⚠️ | 第三方 |
| Cosmos Policy | NVIDIA | — | 微调视频模型做视觉运动规划 | — | 权重未确认 | 第三方 |
| UnifoLM-WMA-0 | Unitree / 2025-09 | — | 世界模型-动作框架 | — | 开源（第三方转述） | 第三方 |

与 [training-pipeline.md](training-pipeline.md) §1.3 U-37 的关系：GE-Act 2.0 是第五家独立验证 WAM 目标的（Dyna-2 / DreamZero / GE-Act / Cosmos Policy / Cosmos 3），且首次给出**从零训练、30,000 h、技能覆盖度→OOD 泛化**的公开曲线。仍无一家公开与纯动作目标的可控消融，U-37 结论不变。

### 3.3 骨架规律

1. **骨干全部来自开放 VLM**：Qwen 系（Qwen2.5-VL / Qwen3-VL / Qwen3.5：RDT2、StarVLA、InternVLA、GR00T N1.7 的 Cosmos-Reason2、UnifoLM）已成 2026 事实标准，PaliGemma（π 系）与 Llama-2（OpenVLA）是上一代。这与 training-pipeline §1.1 "M 档取 Qwen-VL 3B/4B 级"一致。
2. **动作头收敛于流匹配 DiT，参数 0.3B 级**（π0 0.3B、GR00T N1.7 16 层、MolmoAct2、SmolVLA、StarVLA-π）；离散 token 退为预训练桥或 tokenizer 产品（OpenFAST、FAST、RVQ）。GR00T N1.6→N1.7 把 DiT 从 32 层减回 16 层同时把动作维扩到 132、H 扩到 40——**容量投向更宽的槽位与更长的 chunk 而非更深的头**，与我们掩码槽位向量设计相容。
3. **具身统一两派**：GR00T 每具身独立编解码器（N1.7 仍保留）vs 统一槽位（RDT 128 维、GR00T N1.7 的 132 维上限）。我们选后者（training-pipeline §1.2 第 3 条），N1.7 的 132 维给了上限参考。
4. **人类视频进预训练已是开源主流**：GR00T N1.7（20K h EgoScale）、Qwen-RobotManip（含人类视频 + 人→机管线）、MolmoAct2（MolmoER 具身推理语料）。human 轨不再是差异化，**伪动作标签的质量**才是。

---

## 4. 训练框架

| 框架 | 机构 / license | 覆盖模型 | 分布式后端 | 多机 | 数据格式 | 评测集成 | 来源属性 |
|---|---|---|---|---|---|---|---|
| [LeRobot](https://huggingface.co/docs/lerobot/en/hardware_guide) | HF / Apache-2.0 | `act` `vqbet` `tdmpc` `diffusion` `multi_task_dit` `smolvla` `pi0` `pi0_fast` `pi05` `xvla` `wall_x` `groot` `eo1` `sac`（HIL-SERL） | Accelerate（DDP） | 多 GPU；HF Jobs 托管（T4 / L4 / A10G / A100 按秒计费） | LeRobotDataset v3 + 流式 | 无内置基准，靠外部 | 官方文档 |
| [openpi](https://raw.githubusercontent.com/Physical-Intelligence/openpi/main/README.md) | PI / **Apache-2.0** | π0、π0-FAST、π0.5（PyTorch 仅 π0 / π0.5） | JAX：`fsdp_devices` 模型并行；PyTorch：torchrun | **JAX 不支持多机**；PyTorch 多机 torchrun 但无 FSDP / LoRA / 混合精度 / EMA | LeRobot | LIBERO 配方 | 官方 |
| [Isaac-GR00T](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/README.md) | NVIDIA / 代码 Apache-2.0 | GR00T N1.5 / 1.6 / 1.7 | PyTorch | 1+ GPU 40 GB+（推荐 H100 / L40 节点）；DGX Station GB300 单卡 batch 128 | LeRobot 格式 + modality 配置 | Isaac Lab-Arena、LIBERO / DROID / SimplerEnv 微调权重 | 官方 |
| [StarVLA](https://github.com/starVLA/starVLA) | 多机构 / **MIT**，3.8k star | 骨干 Qwen3-VL-4B、Qwen3.5 0.8–9B、Florence-2、Cosmos-Predict2、Wan2.2；头 FAST / OFT / π / GR00T | Accelerate + **DeepSpeed ZeRO-2** | 8→256 A100 实测，>32 卡扩展效率 79–80%；支持 **Ascend NPU** | 自定义 | **12 个基准**：SimplerEnv、LIBERO、LIBERO-plus、RoboCasa-GR1、RoboCasa365、RoboTwin 2.0、DOMINO、BEHAVIOR、CALVIN、RoboDojo、SO101、RLBench | 官方仓库 + 论文 |
| [Dexbotic](https://arxiv.org/abs/2510.23511) | Dexmal / 未核 | π0、OpenVLA-OFT、CogACT 等，附更强预训练基座 | PyTorch | 未说明 | — | — | 论文 |
| [VLA Foundry](https://arxiv.org/abs/2604.19728) | TRI / **未注明** | LLM→VLM→VLA 从零训练 + Qwen3-VL 骨干；两个权重已放 | **FSDP2** + WebDataset 流式 | 多机（AWS SageMaker）+ 本地 torchrun | WebDataset | LBM Eval 闭环 + STEP 分析 | 论文 + 第三方 |
| VLA-Scratch | 社区（~300 star） | 多 VLM 骨干、异构数据集共训练 | **FSDP2** + Hydra + torchrun | 未确认 | — | — | 第三方 |
| FluxVLA | LimX Dynamics | — | FSDP 多机 | 支持；LIBERO 多机并行闭环仿真 | — | LIBERO | 官方文档 |
| RoboVerse / MetaSim | UC Berkeley 等 | OpenVLA 等 IL/RL/VLA 工作流 | torchrun 单机 | 未支持 | 自定义 | 多仿真器统一 | 官方文档 |
| Isaac Lab（RLinf） | NVIDIA | GR00T / OpenVLA 的 RL 后训练 | — | — | — | Arena 批量评测 | 见 research-opensource §6 |
| JoyNexus | 京东 / 论文 | 多租户 VLA 后训练服务 | — | — | — | — | 论文（[arXiv:2607.16074](https://arxiv.org/pdf/2607.16074)） |

**对 [training-pipeline.md](training-pipeline.md) §3.1 的判断**：Stage A（单卡微调）维持 LeRobot + openpi；Stage B（M 档 0→1 预训练）**候选从 LeRobot 单一路线扩为 LeRobot vs StarVLA**——StarVLA 的 Qwen3-VL-4B 骨干正是我们 M 档选型、四种动作头可直接做"离散桥→流匹配"课程消融、12 个基准省掉 eval-CI 一半工程，MIT 许可无障碍；缺点是数据格式自定义（需写 LeRobot v3 适配器）、依赖 DeepSpeed 而非 FSDP。openpi 的 JAX 路线因**不支持多机**不适合 Stage B。登记为 U-44。

---

## 5. 资源消耗

### 5.1 预训练算力（补 [research-vla-pretraining.md](research-vla-pretraining.md) §3.2 没有的）

| 训练 | 算力 | 来源属性 |
|---|---|---|
| **GR00T N1.7 3B 预训练** | **64 节点 × 4 GB200 × 120 h = 30,720 GPU·h**，41,288 kWh，16.9 tCO₂e（模型卡标注"内部估算"） | 官方模型卡 |
| GR00T N1.6 预训练 | 300k 步 × 全局 batch 16,384；GPU 数与时长未披露 | 第三方博客 ⚠️ |
| StarVLA-GR00T（Qwen3-VL-4B）RoboCasa-GR1 | 8×A100 80GB：100k 步 **20.4 h**（batch 64）= 163 A100·h；256×A100：100k 步 25.9 h（batch 2048）= 6,630 A100·h，>32 卡效率 ~80% | 论文 |
| StarVLA 各基准标准训练 | LIBERO 8×A100 30k 步；SimplerEnv / RoboCasa-GR1 16×A100 100k 步；RoboTwin 2.0 **48×A100 150k 步** | 论文 |
| Cosmos 3 | 20T 多模态 token；GPU 小时未披露 | 第三方 |
| GE-Act 2.0 | 30,000 h 数据从零训练；GPU 未披露 | 论文 |
| EgoScale（NVIDIA） | 20,854 h 人类视频预训练；GPU 未披露 | 论文 |

量级更新：3B 级 VLA 预训练的公开锚点现在有三个——GR00T N1 ~50k H100·h（2025）、N1.7 30.7k GB200·h（2026，GB200 单卡约 2–3× H100 吞吐，等效 6–9 万 H100·h）、RDT-1B 35k H100·h——**稳定在 1e4–1e5 GPU 小时**，research-vla-pretraining §3.2 的结论不变。StarVLA 的数字说明**单基准专家模型只要 1e2–1e3 GPU 小时**。

### 5.2 微调：显存与时间

| 模型 / 框架 | 推理显存 | LoRA 微调 | 全参微调 | 实测时长 | 来源属性 |
|---|---|---|---|---|---|
| LeRobot 分组（batch 8，AdamW） | — | — | Light BC（act / vqbet / tdmpc）**2–6 GB**；Diffusion **8–14 GB**；SmolVLA **10–16 GB**；Large VLA（pi0 / pi05 / xvla / wall_x）**24–40 GB**；groot / eo1 **24–40 GB** | 50 条 × 5 epoch：act 单 4090 30–60 min；diffusion 2–4 h；smolvla 单 A100 1–2 h；pi0/pi05 单 A100 4–8 h；**4×H100 5k 步 batch 32：diffusion 16 min、smolvla 28 min、pi05 3 h 41 m**（update 2.55 s/步，梯度检查点 + bf16） | 官方文档 |
| openpi（π0 / π0.5） | >8 GB（4090） | **>22.5 GB**（4090） | **>70 GB**（A100 80 / H100） | 社区：π0.5 全参 4×H100 30k 步 batch 32 ≈ 4 h 25 m；单 A100 10k 步 batch 16 ≈ 8 h 23 m（2.81 s/步） | 官方 README + 第三方 |
| GR00T N1.7 | **16 GB+**（4090 / L40 / H100 / **Jetson AGX Thor / Orin** / DGX Spark） | — | **40 GB+**（推荐 H100 / L40；A6000 可但慢）；第三方课程称仿真微调 ≥48 GB | — | 官方 README |
| RDT2 | ~16 GB（4090）+ >32 GB 内存 | VQ 版 LoRA **>32 GB**（A100 40）；FM 专家微调 ~16 GB | VQ 版 **>80 GB**（A100 80 / H100 / B200） | — | 官方 README |
| OpenVLA-OFT 7B | 15.9–18.0 GB（bf16） | LoRA + DDP：LIBERO 单图 batch 1 最低 25.6 GB，推荐 44.1 GB（batch 8/卡）；ALOHA 3 图 + FiLM 推荐 73.5 GB | — | **8×A100/H100 80GB，50k–150k 步，1–2 天/任务**（≈200–400 GPU·h） | 官方页 |
| SmolVLA | — | — | 单 A100 20k 步 ≈ 4 h | — | 第三方转述官方指南 |

结论：**单任务后训练是 1e1–1e2 GPU 小时的事，单张 80 GB 卡即可起步；只有 7B 级（OpenVLA-OFT、RDT2-VQ）才需要 8 卡节点。** 这支持 training-pipeline §2 Stage A 的"单卡 LoRA"口径，也给 [program-plan.md](program-plan.md) 的算力预算提供锚点。

### 5.3 推理（[VLA-Perf](https://arxiv.org/html/2602.18397v1)，2026-02）

| 硬件 | π0（2.7B）端到端延迟 / 频率 | π0-L 9.1B | π0-XL 16.7B |
|---|---|---|---|
| **Jetson Thor** | 52.6 ms / **19.0 Hz** | 3.9 Hz | 2.1 Hz |
| RTX 4090 | 31.1 ms / 32.2 Hz | 8.0 Hz | OOM |
| A100 | 16.2 ms / 61.7 Hz | — | — |
| H100 | 6.2 ms / 162.5 Hz | — | — |
| B100 | 3.2 ms / 314.4 Hz | 73.6 Hz | 39.7 Hz |

要点：动作专家受内存带宽限制、视觉 + VLM 受算力限制；延迟随参数量近线性；**去噪步数强烈影响延迟而 chunk 大小几乎不影响**；分块扩散比逐 token 自回归快 1–2 个量级（B100 上 3.2 ms vs 327.6 ms）；长上下文（KV 缓存历史帧）在数据中心卡可到 1K 步、边缘卡 ~100 步；**服务端推理（即便消费卡）通常优于机上推理，除非网络极差**：B100 同步服务 10G 以太网 301 Hz、WiFi 7 120 Hz、5G 36 Hz、4G 14 Hz。

对 [runtime-and-deployment.md](runtime-and-deployment.md) 的含义：S1 等价层若要 100 Hz，机上 3B 级模型做不到（Thor 19 Hz），必须靠动作 chunk 外推 + 异步推理，或把 VLM 放到站内服务器——与 Figure 把 S2 放 7–9 Hz、S1 跑 200 Hz 的分层设计一致（[research-model-recipes.md](research-model-recipes.md) §1）。

### 5.4 存储量级

| 数据 | 体量 | 换算 |
|---|---|---|
| AgiBot World 2026 | 13.6 TB（9 路相机含鱼眼/深度、LeRobot v2.1 mp4） | 官方卡未给小时，无法换算 |
| Egocentric-10K | 16.4 TB / 10,000 h / 1.08B 帧 | **~1.6 TB / 千小时**（单路视频，无音频） |
| RDT-1B 预训练集 | 46 数据集 21 TB | — |
| Dyna 车队回流 | >1 TB / 站 / 天（自报，D-26） | 对照 [data-platform.md](data-platform.md) 容量模型 |

单路第一视角视频 ~1.6 TB/千小时是 human 轨容量模型的直接锚点；多路相机的人形 robot 轨按路数线性放大，加深度与触觉后再乘 1.5–2（AgiBot 2026 的 9 路配置可作上界参考）。

---

## 6. 对本仓库的启示与回写清单

1. **Stage A 候选导入集（U-43）**：UnifoLM-WBT（G1 全身，若核实 Apache-2.0）是唯一"人形 + 全身 + 商用可用"的开放集，应作为 ingest robot 轨与 export 的首个外部回归样本；Humanoid Everyday（CC BY 4.0，G1 Dex3-1 带触觉）第二；AgiBot World 2026（NC）只进研究分支做 QC 门校准。导入即验证 data-format-contract 对 LeRobot v2.1 → v3 的兼容。
2. **评测协议修订（R-26）**：LIBERO 审计失败 → eval-protocol §2 把 LIBERO 降为参考项，主回归改 RoboCasa-GR1 + LIBERO-Plus + RoboTwin 2.0 子集；真机协议对齐 RoboArena 盲测成对比较。否则我们的消融裁决（决策 4"阈值改动必须走消融"）会建立在捷径可解的基准上。
3. **Stage B 框架选型（U-44）**：LeRobot vs StarVLA，见 §4 判断。
4. **算力预算校准**：M 档 3B 预训练 3e4–1e5 GPU·h、单任务后训练 1e1–1e2 GPU·h、7B 级后训练需 8 卡节点；边缘推理 3B 级 ~20 Hz（Thor）。写入 program-plan 预算与 runtime 延迟预算。
5. **human 轨伪标签是必建件**：开放大集无手部标注（Egocentric-10K）或不开放（EgoScale）；EgoScale 证明伪标签噪声可被规模摊薄但需如实记录——我们 human 轨 schema 的置信度字段必须保留。
6. **WAM 第五家**：GE-Act 2.0 加入 U-37 的证据链（从零训练 30,000 h 曲线），结论仍为可选分支。
7. **自报数字登记**：D-28 Cosmos 3 "RoboArena 第一"（厂商自称）；D-29 Build AI Egocentric-100K / 1M 规模（单一博客）；D-30 X-Humanoid "700+ 任务 / 对外交付 3 万小时"、Qwen-RobotManip "RoboChallenge 第一 +20%"（论文自报、权重不可核）。均无设计依赖，仅作量级。
8. **license 待核清单**（引入前必办）：UnifoLM-WBT、MolmoAct2、RDT2、OpenVLA/OFT、DROID、RoboMIND 2.0、EgoDex、Dexbotic、VLA Foundry。

---

## 7. 来源

**数据集**：[OXE](https://arxiv.org/abs/2310.08864) · [DROID](https://arxiv.org/abs/2403.12945) · [RoboMIND](https://arxiv.org/abs/2412.13877) / [2.0](https://arxiv.org/abs/2512.24653) · [AgiBot World 2026 数据卡](https://huggingface.co/datasets/agibot-world/AgiBotWorld2026) / [公告](https://agibot.com/article/231/detail/54.html) · [Galaxea](https://arxiv.org/abs/2509.00576) · [Humanoid Everyday](https://arxiv.org/abs/2510.08807) · [UnifoLM-WBT 集合](https://huggingface.co/collections/unitreerobotics/unifolm-wbt-dataset) / [澎湃报道](https://m.thepaper.cn/newsDetail_forward_32879404) · [MolmoAct2](https://arxiv.org/abs/2605.02881) · [BEHAVIOR Challenge](https://behavior.stanford.edu/challenge) · [LeRobot Hub 58k](https://www.techtimes.com/articles/317129/20260525/open-source-robotics-ai-reaches-inflection-point-lerobot-hub-surpasses-58000-datasets-in-one-year.htm) · [Egocentric-10K 数据卡](https://huggingface.co/datasets/builddotai/Egocentric-10K) / [Humanoids Daily](https://www.humanoidsdaily.com/news/build-ai-open-sources-10-000-hours-of-factory-worker-video-to-scale-robot-learning) / [Labellerr 汇总](https://www.labellerr.com/blog/egocentric-datasets-robotics/) · [EgoDex](https://www.iclr.cc/virtual/2026/poster/10010617) · [EgoScale](https://arxiv.org/abs/2602.16710) · [Ego-Exo4D IJCV](https://link.springer.com/article/10.1007/s11263-025-02557-6) · [InternData-A1](https://arxiv.org/abs/2511.16651) · [RoboCasa365](https://arxiv.org/abs/2603.04356) · [数据金字塔表](https://github.com/worldbench/awesome-embodied-data-pyramid)

**基准**：[基准审计](https://arxiv.org/abs/2606.04233) · [RoboChallenge](https://arxiv.org/html/2510.17950v1) / [年报 deck](https://speakerdeck.com/takasumasakazu/robochallenge-en) / [量子位 2026-01](https://www.qbitai.com/2026/01/374597.html) · [RoboArena](https://arxiv.org/abs/2506.18123) · [PhAIL](https://arxiv.org/pdf/2605.29710) · [BEHAVIOR-1K](https://arxiv.org/abs/2403.09227) · [LIBERO-Plus](https://www.sourcepulse.org/projects/26294051) · [vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)

**模型**：[openpi README](https://raw.githubusercontent.com/Physical-Intelligence/openpi/main/README.md) / [LICENSE](https://raw.githubusercontent.com/Physical-Intelligence/openpi/main/LICENSE) · [Isaac-GR00T README](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/README.md) / [N1.7 模型卡](https://huggingface.co/nvidia/GR00T-N1.7-3B) / [N1.6 第三方](https://www.naddod.com/ai-insights/a-deep-dive-into-pre-training-and-post-training-for-nvidia-isaac-gr00t-n1-6) · [RDT2 README](https://raw.githubusercontent.com/thu-ml/RDT2/main/README.md) · [OpenVLA-OFT](https://openvla-oft.github.io/) / [论文](https://arxiv.org/abs/2502.19645) · [InternVLA-A1](https://arxiv.org/abs/2601.02456) / [模型卡](https://huggingface.co/InternRobotics/InternVLA-A1-3B/blob/main/README.md) · [Qwen-RobotManip](https://arxiv.org/pdf/2606.17846) / [MarkTechPost](https://www.marktechpost.com/2026/06/16/meet-qwen-robotsuite-three-embodied-ai-models-for-vla-manipulation-video-world-modeling-and-navigation/) · [MiniCPM-RobotManip](https://huggingface.co/openbmb/MiniCPM-RobotManip) · [GE-Act 2.0](https://arxiv.org/abs/2609.05588) · [Cosmos 3 第三方](https://techjacksolutions.com/ai-brief/nvidia-cosmos-3-checkpoints-are-live-the-technical-report-li/) · [DreamZero](https://www.sourcepulse.org/projects/24812067) · [π0.6 社区复现](https://huggingface.co/exla-ai/openpie-0.6)

**框架与资源**：[LeRobot 硬件指南](https://huggingface.co/docs/lerobot/en/hardware_guide) · [StarVLA 论文](https://arxiv.org/html/2604.05014v1) / [仓库](https://github.com/starVLA/starVLA) · [Dexbotic](https://arxiv.org/abs/2510.23511) · [VLA Foundry](https://arxiv.org/abs/2604.19728) · [VLA-Scratch](https://www.sourcepulse.org/projects/23589909) · [FluxVLA](https://www.limxdynamics.com/en/documents/825076533948452864) · [RoboVerse](https://roboverse.wiki/roboverse_learn/imitation_learning/openvla) · [VLA-Perf](https://arxiv.org/html/2602.18397v1) · [openpi 社区微调记录](https://huggingface.co/q-research/pi05-base-mini-chair-openpi)
