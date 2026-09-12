# SimFoundry（NVIDIA GEAR）调研：单视频→仿真场景的 real2sim2real 管线

> 2026-09-09。来源：论文 [arXiv:2606.28276](https://arxiv.org/abs/2606.28276)（2026-06-26 提交，NVIDIA GEAR + Stanford + Georgia Tech + UT Austin，Ajay Mandlekar / Yuke Zhu 共同指导，Li Fei-Fei 合著）、[项目页](https://research.nvidia.com/labs/gear/simfoundry/)、[GitHub NVlabs/SimFoundry](https://github.com/NVlabs/SimFoundry)（2026-08-14 开源 V0，Apache-2.0，含 THIRD_PARTY_LICENSES.md）、[示例资产 HF 数据集](https://huggingface.co/datasets/nadunRanawaka1/simfoundry-assets)。可信度：**学术论文 + 开源代码，数字可复现性高于公司自报**；但作者方即 GR00T/DexMimicGen 团队，评测用的策略（GR00T N1.6/1.7、DreamZero）多为自家模型，需注意。与本仓库分工：sim 轨见 [sim-track.md](sim-track.md)，评测见 [eval-protocol.md](eval-protocol.md)。

## 0. 一句话

给一段手机拍的桌面场景视频，SimFoundry 全自动（约 5 分钟/物体）产出物理可用的仿真数字孪生（OmniGibson/Isaac Lab），再用 VLM 生成"数字表亲"（物体/布局/任务三轴变体），用于**在仿真里评测真机策略**（与真机成功率 Pearson 0.911）和**生成仿真训练数据零样本迁移真机**（DROID Stack Dishware 100%、YAM Pot on Stove 99%）。它是 GR00T 数据金字塔"仿真中层"的场景来源，位置正好填我们 sim-track §2 资产管线的空白。

## 1. 管线（三段、13 个阶段、全部换件式）

| 段 | 做什么 | 用的模型（论文 E.2，均可替换） |
|---|---|---|
| **Extraction** | 视频 → 代表帧 → 深度 → 点云；地面分割对齐世界系；VLM 列物体 → 逐个分割 → 抠掉（图像+深度补全）→ 迭代直到没有前景 | 深度 Depth Anything 3（单目）/ FoundationStereo（双目）；分割 SAM3；场景理解 Gemini-Pro-3；深度补全 PriorDepthAnything |
| **Generation** | 每个物体裁图 → 超分 → 2D→3D 网格；6D 位姿对齐到点云并精修；可动物体（抽屉/柜门）单独走关节生成；CoACD 生成碰撞体；VLM 赋质量/摩擦；PyBullet 去穿模、落稳；导出 USD/OmniGibson/Isaac Lab | 网格 Hunyuan3D-2.1（默认）/ TRELLIS.2 / Pixal3D；位姿 FoundationPose；网格分部件 P3-SAM / PartField；关节参数 Gemini + articulate-anything |
| **Augmentation** | 数字表亲：**物体表亲**（按功能部件分解后在几何/拓扑/外观三维度提案 → 图像编辑模型生成 → 再 2D→3D）、**场景表亲**（用 OnTop/Inside/RightOf 等谓词重排布局 + 加干扰物）、**任务表亲**（VLM 给场景图 + 物体表 + 机器人约束 + 允许谓词集合 → 提出 N 个需要状态改变的任务 → 编译成可直接跑数据生成的目标谓词文件） | Gemini-Pro-3 / Gemini-Pro-3-Image-Preview |
| 背景（可选） | 自动：SAM2 传播掩码 + VOID 两遍视频补全 → 干净背景流 → 深度监督 3D 高斯泼溅 → 刚性变换进仿真（单卡约 90 分钟/场景）；手动：再拍一段清空桌面的视频训练 splat，在编辑器里对齐 | SAM2、VOID（CogVideoX 权重）、Nerfstudio/3DGRUT |

代码组织：Pipeline A（重建 13 阶段）/ B（表亲 + 任务提案）/ C（OmniGibson 加载、遥操作采集、评测、烟测）+ 浏览器轻量场景编辑器 + OmniGibson 内交互编辑器。Hydra 配置每个阶段。**数据生成与策略训练代码尚未开源**（README 明示 "Not yet released"）。

## 2. 关键数字（论文口径）

### 2.1 real→sim 评测（仿真能不能替真机打分）

- 7 个任务（DROID 单臂 Franka：Cup in Bowl / Marker in Cup / Serve Fruits / Clear Table / Stack Dishware / Store Marker / Throw Away Trash；YAM 双臂平台）× 5 个策略（π0、π0.5、GR00T N1.6、GR00T N1.7、DreamZero）；简单 4 任务零样本部署，难 3 任务每任务 50 条真机演示微调。
- **mean Pearson r = 0.911，MMRV（最大排名违反）= 0.018**（摘要另一处写 0.928，以正文 Table G.1 的 0.911 为准）；子任务级评测把 r 从 0.90 提到 **0.95**。
- 对比 PolaRiS（2025 SOTA real2sim 评测）：SimFoundry 的 Pearson **高 0.59 以上**。
- 只报二值成功率不报归一化奖励，理由是成功率是更严格的保真度检验（FAQ 7）。
- 评测揭示模型差异：GR00T N1.7 精细抓取强（Marker in Cup），π0.5 语言跟随强（Serve Fruits）。

### 2.2 sim→real 训练（仿真数据能不能训出真机策略）

- 数据生成配方（H.1）：每任务 **10–15 条人类遥操作演示**（JoyLo）→ **MimicGen 增殖** + 域随机化（材质、相机位姿、DROID 加桌高）。
- 零样本迁移：YAM Pot on Stove **99%**（从零训的流匹配策略）；DROID Stack Dishware **100%**（微调 π0.5-DROID 检查点）。注意 FAQ 6：预训练检查点本身在 Store Marker / Throw Away Trash 上 **0%**，说明收益来自仿真微调数据而非基座。
- 仿真 + 少量真机共训：π0.5 Store Marker 真机 60% → **92%**。
- 物体表亲：held-out 物体上 Pot on Stove **+50 个百分点**；DROID Throw Away Trash 最多 +20。
- 场景表亲：Throw Away Trash 仿真 +28；Store Marker 表亲布局 0% → 16%。
- 任务表亲/多任务：一个杂乱场景由 VLM 提 13 个任务纯仿真生成数据微调 π0.5，13 个已见任务真机 28% → 46%，**7 个 held-out 任务 0% → 29%**（π0.5-FT）；总演示数固定时，用相关任务表亲替换部分目标任务数据，仿真 Throw Away Trash +60%、Store Marker +40%。

### 2.3 系统指标

- 重建保真：全自动 F1 0.81–0.92（SAM3D 0.66–0.71）；每物体再加 **3 分钟人工微调** F1 升到 0.93–0.99。
- 速度：**约 5 分钟/物体**（整条管线摊销）；自动背景另需约 90 分钟/场景（可并行）。
- 硬件：Linux + NVIDIA GPU；24 GiB 卡可跑（网格阶段需 low_vram），默认网格阶段约 29 GiB；全量安装约 250 GB 磁盘；需 HF 账号（多个 gated 模型）+ Google Vertex AI 或 Gemini API key。

## 3. 局限（论文自述 §6 / 附录 C）

1. 完全依赖现成基础模型，继承各自失效模式；VLM 走远程 API，**同输入不同输出（非确定）**，偶发补全出退化/重复物体。
2. 单目输入的尺度与形状可能不准；关节生成依赖网格 3D 分割，遮挡内部结构时困难。
3. 物理稳定流程假设物体都放在**单一水平面**上，**仅限桌面式布局**（多层/非平面场景是未来工作）。
4. 3DGS 背景近场裁剪与渲染延迟问题，机器人实验里改用网格背景（Scaniverse 扫描）。
5. 未开源部分：数据生成、训练、评测代码（"Coming Soon"）。

## 4. license 边界（对我们最要紧）

仓库自身 Apache-2.0，但**默认安装链里多件必需组件是非商用或非 OSS**（THIRD_PARTY_LICENSES.md 原文）：

| 组件 | 是否必需 | 条款 | 后果 |
|---|---|---|---|
| Hunyuan3D-2.1（默认网格模型） | 必需 | 腾讯社区许可，**EU/UK/韩国无授权** | 商用需评估；可换 **TRELLIS.2（MIT）** 或 Pixal3D（MIT） |
| FoundationPose / FoundationStereo | 必需 | NVIDIA Source Code License，**非商用** | 商用阻塞；位姿精修需替代（Any6D 也是学术限定） |
| nvdiffrast | 必需 | 非商用（第三方） | 同上 |
| SAM3 | 必需 | Meta SAM License，非 OSS、gated | 需审条款；SAM2 是 Apache |
| Gemini（场景 VLM / 图像编辑） | 必需（VLM 阶段） | Google API ToS | 输出用于训练数据的条款要审（与我们 R-09 同类） |
| VOID 权重（CogVideoX License）、DINOv3、PartField、CoTracker、RMBG-2.0 | 可选/背景/关节 | 各自 gated 或非商用 | 不走这些路径即可 |
| PyMeshLab、plyfile | 依赖 | **GPL-3** | 服务端自用可，分发件不得链接 |
| Isaac Sim / Kit / NuRec | 运行时 | NVIDIA Omniverse License | 与我们 Isaac Lab 选型同一条款 |
| OmniGibson、BDDL、CoACD、Depth Anything 3、SAM2、TRELLIS.2、cuRobo、LeRobot | | MIT / Apache | 干净 |

结论：**研究分支可以整套跑；商用默认路径必须换掉 Hunyuan3D-2.1（→TRELLIS.2）与 FoundationPose（待找 Apache 级替代或自研 ICP 精修），并把 Gemini 换成本地 Qwen-VL**——它的模块化设计正好允许这么换，但换件后的保真度需自己复测。

## 5. 对本仓库的启示

1. **sim 轨资产管线有了具体方案**：[sim-track.md](sim-track.md) §2 原本只有"开源资产库 + 手机扫描"，SimFoundry 给出了从**我们自己的采集视频**（human 轨头戴视频、robot 轨场地相机、Creator 手机视频）直接生成仿真孪生的路径。采集环境=部署环境=仿真环境，三者同源，这是 Figure "Brookfield 场地既采数又部署"思路的仿真延伸。
2. **真机评测的仿真替身**：[eval-protocol.md](eval-protocol.md) §2 的"Isaac Lab-Arena 自建任务集（与真机任务模板一一对应）"应改为**用 SimFoundry 从真机评测场地的视频重建**，这样 sim-real gap 探针（§5）有了可对照的基线（Pearson 0.911 / MMRV 0.018 是目标值）；子任务级评测与我们 curation 的子任务分割天然对齐（把成功率拆到 segment 级）。
3. **任务表亲 = 任务模板的自动生成器**：index-replica-plan §2 的任务市场目前靠人写模板；VLM 从场景图 + 物体表 + 机器人约束提出"需要状态改变"的任务并编译成谓词目标，可以反过来给 Creator App 与 robot 轨生成任务模板（谓词形式还能直接当成功判据）。
4. **数据生成配方印证 sim-track §3**：10–15 条遥操作种子 + MimicGen 增殖 + 域随机化 → 零样本迁移，与我们"DexMimicGen 增殖 100–1000×"一行一致；增殖物体应换成表亲而不只是位姿扰动（物体表亲 +50 点是最大单项增益）。
5. **限制决定用法**：仅桌面布局 → 覆盖我们操作任务簇（台面家务），不覆盖全身/移动/多层场景；VLM 非确定 → 场景生成结果必须**版本化入 lineage**（配置哈希 + 生成物哈希），与 sim-track §4 随机化版本化同一纪律。
6. **license 时序**：H0 研究分支可直接用；进入默认路径前需完成 §4 的换件，登记为 governance U-20，并把 Hunyuan3D-2.1 / FoundationPose / SAM3 / Gemini ToS 加进 U-11 核查表。
7. **S2 高层规划 / 长任务推理语料（我们的推断，SimFoundry 未验证）**：孪生场景自带符号级状态真值（物体表、OnTop/Inside/RightOf 谓词、任务表亲的谓词目标），OmniGibson 原生支持 BDDL（BEHAVIOR-1K 1,000 个家务活动定义）做目标校验。由此可自动产出规划四元组：观测序列 + 任务指令 + 子任务序列 + 逐步谓词状态与完成标签，全部为仿真校验真值——这是真实数据永远给不了的。三类用法：(a) **规划轨迹**：VLM 提任务 → 谓词目标 → 脚本执行器（cuRobo + OmniGibson 动作原语，不依赖其未开源的训练代码）→ 逐步子目标判定，作为 S2 SFT 语料兼 curation 分层标注/子任务分割的金标准；(b) **失败与重规划**：受控注入扰动（物体被挪、抽屉卡住、抓取失败）产生"计划→失败→重规划"轨迹，真实数据几乎没有；(c) **长任务评测**：同场景多个任务表亲链成长任务，自动打子任务进度分与扰动恢复率。边界：论文所有实验都是底层操作策略，无规划/语言推理实验，0.911 是原子级任务上的数；VLM 提出的任务是模板化措辞，S2 单独在上面训会学到模板，须与 human/robot 轨事后反推标注混合（仿真给接地与校验，真实数据给语言多样性）；仅桌面布局，跨房间导航+操作的长任务建不出来。落地：sim-track §3 `planning_trace`、architecture §3.1、curation §4.1、eval-protocol §2，验证假设登记 governance U-21。
8. **Creator App 侧用法（index-replica-plan §2）**：Creator 入网时用手机拍 30–60 s 台面/操作区视频（与 P0 手机方案同一设备），服务端跑 SimFoundry 得到该 Creator 场景的孪生 + 物体清单 + 谓词状态，随后：(a) **个性化任务生成**——任务表亲只基于这个家里实际存在的物体与可达性提任务（"把台面上的蓝色马克杯放进右侧抽屉"），替代通用模板；(b) **谓词级完成判据**——每个任务自带目标谓词（Inside(mug, drawer)），App 端上或入湖时用起止帧 + VLM 对照谓词判定完成，计酬锚定"通过判据"，比现在 L3 三问式语义审计更客观；(c) **多样性 KPI 变实体计数**——`object_tags`/`environment_tags` 从重建物体清单写入而非 VLM 猜测，再平衡可以精确指向"缺木质抽屉的厨房场景"并下发到有该物体的 Creator；(d) **每个 Creator 场景同时成为 sim 轨孪生**——家庭场景的评测替身与表亲数据顺手获得（§5.1/§5.2），采集环境=仿真环境=部署环境。成本：约 5 分钟/物体 GPU，一个台面 15–30 个物体 ≈ 1–2.5 GPU·h，一次性 + 场景变化时增量重建；每场景若干次 Gemini/本地 VLM 调用。边界：只重建台面级操作区，不是整屋；家居 3D 孪生（物体清单 + 布局）属敏感个人数据，需单独同意、按 `region` 驻留、随删除请求传导（compliance §3）；VLM 提任务非确定，任务模板须版本化并经人工抽检后再下发；商用默认路径同样受 §4 license 换件约束。登记 governance U-22。
9. **诚实性提醒**：评测策略半数是作者团队自家模型（GR00T、DreamZero），0.911 的相关性是在 7 个桌面任务上得到的；我们的复现目标先定在自家 3 个任务 ≥0.8。

## 6. 与相关工作的关系

- **digital-cousins / ACDC**（Stanford，Apache）：SimFoundry 的上游，"数字表亲"概念与部分代码来源。
- **PolaRiS**（2025）：real2sim 评测基线，被 SimFoundry 以 +0.59 Pearson 超越。
- **SAM3D**：单模型 2D→3D 场景重建基线，SimFoundry 在杂乱/遮挡场景更准（Chamfer/位置误差表）。
- **GR00T / DexMimicGen / DreamGen / FLARE**：同一 GEAR 实验室；SimFoundry 补的是"场景从哪来"，DexMimicGen 补"轨迹从哪来"，DreamGen 补"神经轨迹"。三者合起来就是 sim-track §3 的三个 `source`。

已同步到：[sim-track.md](sim-track.md) §1/§2/§3/§5、[eval-protocol.md](eval-protocol.md) §2/§5、[governance.md](governance.md) U-20/U-21/U-22 与 U-11 第 19–22 行、[architecture.md](architecture.md) §3.1、[curation-pipeline.md](curation-pipeline.md) §4.1、[index-replica-plan.md](index-replica-plan.md) §1.0 采集矩阵/§2/§7、[architecture.md](architecture.md) §7 采集层、[program-plan.md](program-plan.md) §2、[data-format-contract.md](data-format-contract.md) §1.3、CLAUDE.md 决策 2、[compliance-and-security.md](compliance-and-security.md) §3、[data-platform.md](data-platform.md) §1.3（2026-09-09）。
