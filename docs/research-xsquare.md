# 自变量机器人（X Square Robot）数据管线调研

> 2026-11-02。一手来源 13 份已归档到 [sources/xsquare/](sources/xsquare/)（清单见 [sources/MANIFEST.md](sources/MANIFEST.md)），包括三篇技术报告（Wall-OSS-0.5、XRZero-G0、X2Real）、四篇公司新闻稿（XRZero-G0 开源、QUANXTA Zero、WRC 2026、TwinDEX）、两个 GitHub README、官网研究时间线与新闻列表、Hugging Face 组织清单。引用时给出文件里可 grep 的英文原句片段。第三方转述单独标 ⚠️ 并给 URL。
>
> 本文是已有两篇的上层综述：模型侧的清洗五步见 [research-vla-pretraining.md](research-vla-pretraining.md) §1.8，TwinDEX 硬件见 [research-twindex.md](research-twindex.md)。本文把它们和 2026-04 之后的新披露（XRZero-G0、QUANXTA Zero、X2Real、WALL-B）串成一条完整管线。
>
> 数字除特别说明外都是**公司自报**，实验条件由公司自己设定，未见独立复现。

## 0. 结论先行

1. **自变量的数据管线是"无本体采集为主、真机做锚"的闭环**：采集端有三条线（真机遥操、UMI/VR 式无本体设备、TwinDEX 孪生灵巧手），外加一条仿真合成线。中段是"同步 → 自动清洗 → 人机协同质检 → 标注"。末端用"配比律"把无本体数据和少量真机数据混合，评测再把弱项反馈回采集。2026-07 起，这条链路以 **QUANXTA Zero** 的名义产品化对外销售（[sources/xsquare/quanxta-zero-launch.txt](sources/xsquare/quanxta-zero-launch.txt)）。
2. **最值得抄的三件事**：
   - **物理回放验证**：每个任务类别随机抽一部分轨迹，在目标真机上开环回放，以任务能否完成作为数据是否有效的最终判据（"replayed strictly open-loop"）。
   - **按比例做配比消融**：真机与无本体数据按 1:1 / 10:1 混合，对照纯真机基线，并保持总量可比。
   - **具身桥接样本**：从动作轨迹自动合成 1,200 万条多模态 VQA 样本，让多模态监督和动作数据出自同一批轨迹。
   我们的管线都还没有这三项（§9）。
3. **最需要警惕的三个数字**：数据成本降到"1/20"、"降低 60%"、"几百条无本体数据完成后训练"。三个都是公司在自选任务上测出来的；"1/20"和"60%"的口径也不一致（§8）。开放的 XRZero-G0-3K 数据集只有 34 GB、10,726 行、没有数据卡，和"2,000 小时"对不上（§7）。

## 1. 公司与时间线（只列和数据管线有关的）

| 日期 | 事件 | 来源 |
|---|---|---|
| 2025-09-08 | WALL-OSS 开源（flow / FAST 两个分支），训练代码 wall-x 基于 LeRobot 数据格式 | [wall-x-readme.txt](sources/xsquare/wall-x-readme.txt) |
| 2026-04-15 | XRZero-G0 论文（arXiv:2604.13001）：无本体采集框架 + 2,000 h 数据集 + 配比律 | [xrzero-g0-paper.txt](sources/xsquare/xrzero-g0-paper.txt) |
| 2026-04-21 | WALL-B 发布："世界统一模型 WUM"，视觉/语言/触觉/动作/物理预测联合训练；宣布 35 天后进入家庭 | 第三方 ⚠️ [爱范儿](https://www.ifanr.com/1663081) |
| 2026-05-28 | Wall-OSS-0.5 开源（arXiv:2605.30877），技术报告公开清洗五步与采样配方 | [wall-oss-0.5-report.txt](sources/xsquare/wall-oss-0.5-report.txt) |
| 2026-05-29 | WALL-WM（世界动作模型，按语义事件边界切分） | [home-research-list.txt](sources/xsquare/home-research-list.txt) |
| 2026-06-10 | XRZero-G0 代码 + G0-Dataset 开源 | [news-xrzero-g0-open-source.txt](sources/xsquare/news-xrzero-g0-open-source.txt) |
| 2026-06-30 / 07-02 | X-Tokenizer（多模态动作分词器）；**QUANXTA Zero** 无本体数采产品线发布 | [home-research-list.txt](sources/xsquare/home-research-list.txt)、[news-list-cn.txt](sources/xsquare/news-list-cn.txt) |
| 2026-07-15 | DMuon 分布式优化器开源，训练提速 30%（自报） | [news-list-cn.txt](sources/xsquare/news-list-cn.txt) |
| 2026-08-03 | HOST：看一条人类视频（平均 29 秒）学会新技能，免训练 | [news-list-cn.txt](sources/xsquare/news-list-cn.txt) |
| 2026-08-19 | WRC 2026：物流分拣 1,816 件/小时、准确率 >98%；与 58 同城合作付费保洁 | [wrc-2026-full-loop.txt](sources/xsquare/wrc-2026-full-loop.txt) |
| 2026-08-27 | WALL-SS：生成式世界模型做仿真，600+ 组 sim/real 配对闭环 rollout 校准 | [home-research-list.txt](sources/xsquare/home-research-list.txt) |
| 2026-09-02 | TwinDEX 新闻稿（一手，补齐 [research-twindex.md](research-twindex.md) 的来源缺口） | [twindex-launch.txt](sources/xsquare/twindex-launch.txt) |
| 2026-10-13 | X2Real 仿真评测基准 v2（arXiv:2609.27449）+ 约 300 h 仿真轨迹数据集 | [x2real-report.txt](sources/xsquare/x2real-report.txt) |
| 2026-10-23 / 11-02 | HF 上出现 `wall-oss-1.0-lite-robodojo` 模型与 `robodojo-memory-annotations` 数据集（内容未披露） | [hf-org-listing.txt](sources/xsquare/hf-org-listing.txt) |

公司的自我定位：自研"数据采集-大模型算法-核心零部件-硬件本体"全栈闭环（[home-research-list.txt](sources/xsquare/home-research-list.txt)）。它在工信部标准周上的提法是"数据应作为'工业品'深度开发"（[news-list-cn.txt](sources/xsquare/news-list-cn.txt)），这和 QUANXTA Zero 新闻稿里的 "industrial-grade data production workflow" 是同一个意思。

## 2. 管线全景

```
采集 ─┬─ 真机遥操（桌面双臂 + 移动操作；家庭/工业/办公 + 受控采集间）
      ├─ 无本体：XRZero-G0 / QUANXTA Zero-G1/G0/E0（头显或头带 + 双夹爪 + 腕相机）
      ├─ 孪生灵巧手：TwinDEX（3 指 9 自由度，7 主动 + 2 被动，含指尖触觉）
      └─ 仿真：Mana / X2Real（Task-DAG 驱动自动合成 + 仿真内遥操）
   ↓  端侧时空对齐（传感器 ≤1 ms，视频帧级 100% 对齐；入库微秒级时间戳 + 插值清洗）
清洗 ── 视觉清洗（模糊帧）→ 静止帧降采样 → IK 可行性 / 关节限位 / 奇异 / 自碰撞过滤 → 真机抽样回放
质检 ── AI 置信度分流：高置信自动入库，低置信转人工复核 → 有效率最高 85%
标注 ── 长轨迹切子任务 + 物体/关键帧语义标注；brief / detailed 两级指令 + LLM 扩写；仿真内谓词自动打帧级标签
隐私 ── 人脸与敏感背景模糊、动态水印、短期访问控制
配比 ── 无本体:真机 1:1（抬上限）/ 10:1（替代 90% 真机）；跨源幂采样 p=0.5；动作:多模态 = 9:1；具身桥接样本
评测 ── 真机 17 任务进度分；X2Real 仿真（与真机线性相关 0.84）；WALL-SS 世界模型仿真
   ↺  按评测找弱场景 → 定向补采
```

来源：采集与质检见 [xrzero-g0-paper.txt](sources/xsquare/xrzero-g0-paper.txt) §3.1–3.2、[quanxta-zero-launch.txt](sources/xsquare/quanxta-zero-launch.txt)；配比与标注见 [wall-oss-0.5-report.txt](sources/xsquare/wall-oss-0.5-report.txt) §3；仿真见 [x2real-report.txt](sources/xsquare/x2real-report.txt) §2.3/§3.3。

## 3. 采集层

### 3.1 真机遥操

自采数据来自两类平台："tabletop bimanual systems and mobile manipulators"，覆盖"数千个不同任务"。场景分两种：非结构化的真实环境（家庭、工业、办公）和受控采集间，后者用来保证 "reproducibility and cross-batch consistency"（[wall-oss-0.5-report.txt](sources/xsquare/wall-oss-0.5-report.txt) §3.1.1）。任务沿三个轴打标签：操作复杂度、轨迹时长、特殊属性（空间推理、柔性物体），标签直接用于后面的配比再平衡。

WALL-B 发布会上，CTO 提出"实验室数据像糖水、真实家庭数据像牛奶"，并称团队进入了**数百个志愿者家庭**采集环境样本（第三方转述 ⚠️ [爱范儿](https://www.ifanr.com/1663081)）。2026-05 起的"X 家庭成员计划"把机器人放进真实家庭做长期交互（[wrc-2026-full-loop.txt](sources/xsquare/wrc-2026-full-loop.txt)），这同时也是一条部署回流的数据来源。

### 3.2 无本体采集：XRZero-G0 → QUANXTA Zero

**XRZero-G0**（研究版，2026-04）：
- **硬件**：PICO 4 VR 头显，提供 inside-out 6DoF 追踪，不依赖视觉 SLAM，因为论文认为后者在弱纹理/动态场景里会漂。头显 RGB 相机提供第一视角，另有两路腕相机，共三视角。两个 VR 手柄刚性固定在两种自制夹爪上：H 形按压式用于大幅抓取，G 形手指驱动式用于精细操作。背包里装边缘计算单元。两只夹爪的间距**按目标双臂机器人的基线标定**（"explicitly calibrated to match the baseline distance of the real robotic arms"）。
- **端侧同步**：边缘单元把语言指令、高频 6DoF 轨迹和 "30Hz multi-view video streams" 做时空对齐后上传。
- **吞吐**：峰值 "93.2 episodes per hour"。对照主从遥操，平均完成时间从 35 s 降到 15 s（简单任务）、75 s 到 40 s（中等）、120 s 到 70 s（困难），即 2.33× / 1.88× / 1.71×。
- **论文自称的定位**：位置精度 ≤4 mm、≥3 视角、视觉/触觉/音频三模态（论文 Table 1 与 UMI 系对比，星级为自评）。

**QUANXTA Zero**（产品版，2026-07，[quanxta-zero-launch.txt](sources/xsquare/quanxta-zero-launch.txt)）三款硬件：

| 型号 | 构型 | 用途 |
|---|---|---|
| Zero-G1（UMI-VIO 版，旗舰） | 单头带 + 双夹爪，去掉背包；磁吸热插拔电池可全天采 | 全身移动操作（移动、双臂、举升），同时采视觉、触觉、音频 |
| Zero-G0（UMI-VR 版） | 即 XRZero-G0：PICO 4 + 双夹爪 + 背包 | 全身移动数据，定位精确稳定 |
| Zero-E0（Ego 版） | 轻量第一视角，**6 路相机** | 场景/环境上下文采集，即我们 human 轨的形态 |

G1 的同步指标："Sensor synchronization is controlled within 1ms, with 100% frame-level video alignment"。吞吐为"近 100 条演示/小时，比传统遥操提升 2.33×"。注意这个 2.33× 和 XRZero-G0 论文里"简单任务"的倍率是同一个数。配套的 QUANXTA Zero App 提供任务市场和数据看板，操作员领任务、看设备状态、一键启停，相当于 Figure Index / 我们 Creator App 的采集端（[data-strategy-roadmap.md](data-strategy-roadmap.md) 供给层 B）。

第三方还报道过"全身移动操作数据采集效率是传统遥控的 33 倍"、"训练数据成本降低 95%"等说法，一手稿里都没有，不采用 ⚠️（[维科号](https://mp.ofweek.com/robot/a356714674667)）。

### 3.3 孪生灵巧手：TwinDEX

TwinDEX 的详见 [research-twindex.md](research-twindex.md)。一手新闻稿（[twindex-launch.txt](sources/xsquare/twindex-launch.txt)）补充了三点：
- **同步记录的模态**："multi-view RGB camera inputs, six-degree-of-freedom wrist poses, finger joint states, and fingertip tactile signals"。确认**有指尖触觉**，原调研未能确认。
- **时延对齐**：团队 "measures delays across sensing, inference, and execution"，让训练时看到的观测-动作关系与部署时一致。这对应我们 [architecture.md](architecture.md) §8 的同步误差预算，但他们把推理与执行时延也纳入了预算。
- **一致性清单**：运动链、关节轴、连杆比例、接触几何、表面材质、外观、传感器位置全部对齐，所以手指状态可以直接映射到机器人关节空间，不需要重定向。
- 核心宣称不变：吞吐最高为真机遥操的 5.3×；"a few hundred robot-free episodes, without any on-robot training data" 即可学会 24 子动作的化学实验（D-04）。

### 3.4 仿真：Mana / X2Real

X2Real（[x2real-report.txt](sources/xsquare/x2real-report.txt)）首先是评测基准，但它的数据管线和我们的 sim 轨直接相关：
- **两种示教来源，一套格式**：仿真内主从臂遥操（30 Hz 控制）和"原子技能 + 运动规划"自动合成，二者 "share the same scene generation, task definitions, DAG runtime, evaluation module, trajectory recorder, and exported data format"。
- **免人工的帧级子任务标签**：每个任务是一张 Task DAG，节点挂成功谓词。谓词第一次为真的那一帧就是子任务边界，所以切分 "neither manual boundary annotation nor post-hoc parsing with an auxiliary model is required"。
- **合成数据的闭环验证**：生成（技能 + cuRobo 规划）和验证（节点谓词）分开做，失败时从最近的成功检查点重采样，片段带 lineage（节点 ID、父样本），最后拼接。
- **规模与构成**：约 300 h，其中 Quanta X1 与 ArtiXon Arm 共 158.1 h 作为主后训练集。ArtiXon 约 80% 遥操、20% 合成，其余本体和挑战任务全部自动合成。数据集 Apache-2.0，LeRobot 格式（[hf-org-listing.txt](sources/xsquare/hf-org-listing.txt)）。
- **反直觉的对照结果**：12 层叠积木任务上，自动合成与遥操各 1,398 条，自动合成平均 3.75 层，遥操 1.90 层。按 DAG 边界改成分段指令后，合成数据升到 4.40 层（最高 10 层）。论文给的解释是：遥操轨迹后期大量低运动的对准/检查段，稀释了定长动作块的监督。这和 Wall-OSS 要做静止帧过滤是同一个理由。
- **sim-real 相关性**：标定视觉、物理与底层控制参数后，仿真分与真机分的线性相关达到 **0.84**。

## 4. 同步与入湖

| 环节 | 做法 | 来源 |
|---|---|---|
| 端侧 | 边缘单元做语言指令 / 6DoF / 30 Hz 多视角视频的时空匹配；G1 传感器同步 ≤1 ms | xrzero-g0-paper §3.1；quanxta-zero-launch |
| 入库 | "high-frequency temporal alignment and interpolation-based cleaning to achieve microsecond-level timestamp alignment" | quanxta-zero-launch 第 1 阶段 |
| 训练取帧 | 各平台内相机流按时间戳同步，保留平台原生的相机数与视角；视频帧取 "nearest-timestamp" 的状态帧配对 | wall-oss-0.5-report §3.1 / §3.1.3 |
| 动作语义归一 | 统一到共享语义 schema：双臂末端位姿、关节位、夹爪、底盘、升降/腰、头；只有关节的数据用 URDF 正解补末端位姿；约定 "x points forward, y left, and z upward"、零旋转为水平开口朝前、"larger gripper values denote wider opening"；欧拉角训练前转 6D | wall-oss-0.5-report §3.1.3 |

**与我们的差异**：我们取帧时对信号流做线性插值（[curation-pipeline.md](curation-pipeline.md) §5），他们用最近邻。他们的"坐标轴/夹爪极性约定"值得直接写进 [data-format-contract.md](data-format-contract.md)：同一本体在不同开源集里夹爪极性相反，是跨源混训的常见噪声来源。

## 5. 清洗与质检

三份来源各给了一套步骤。它们其实是同一条管线在不同阶段的描述：

| 步骤 | XRZero-G0 论文 §3.2（无本体） | QUANXTA Zero 新闻稿（产品化） | Wall-OSS-0.5 §3.1.3（训练侧，全部数据） | 我们的对应 |
|---|---|---|---|---|
| 视觉 | 图像质量评估剔除严重运动模糊帧 | — | 开源集按帧异常过滤 | [curation-pipeline.md](curation-pipeline.md) §1.2 视觉门 |
| 静止 | 位置方差低于阈值的静止帧**降采样**（不是删除） | 去除停顿、准备动作 | 用全局统计归一化后，逐维差值低于阈值的帧删除 | §1.3 只有"静止段占比 >70% 降级"，没有帧级过滤 |
| 运动学 | 按目标本体 URDF 映射到末端空间，IK 过滤关节限位/奇异/自碰撞 | 全身 IK + 碰撞 + 关节限位（新闻稿"Kinematic level"） | 异常末端位姿用正解恢复，恢复不了就丢弃 | §1.3 运动学门（已有） |
| 观测一致性 | — | "multi-view geometric consistency suppresses visual-kinematic misalignment"（XRZero 开源稿） | 相机映射接反→重映射 | §1.4b 跨模态一致性门（部分） |
| 物理回放 | **每个任务类别随机抽一部分，在目标真机上开环回放，以任务完成为最终判据** | "real-robot playback serves as the final validation criterion" | — | **缺** |
| 失败/异常 | — | 去除失败与异常轨迹 | 时间戳连续性、动作-观测合理性 | §1.1 技术门 + §1.5 |
| 人机分流 | — | "AI confidence-based routing"：高置信自动入库，低置信送人工 | — | §9 HITL（有框架，无置信度分流规则） |
| 产出指标 | 有效率最高 85% | 有效率最高 85% | — | 漏斗通过率（§1.2 过渡方案） |

两点判断：
1. **"有效率 85%"是在受控条件下测得的**（一手稿原话 "under controlled experimental settings"）。并且新闻稿里 85% 是 AI 分流加人工复核之后的结果，不是纯自动的。
2. **物理回放是我们唯一完全缺的门**，也是 device 轨质量的最终裁判：IK 可行只说明够得到，回放成功才说明做得成。代价是要占用真机，所以他们按任务类别抽样而不是逐条回放。

## 6. 标注

- **两级指令 + 扩写**：每条 episode 都配一条只写最终目标的简短指令，和一条按时间顺序列出中间子目标与关键动作转换的详细指令，再用 LLM 扩写（保持语义），得到数千条基础指令和数万条改写（[wall-oss-0.5-report.txt](sources/xsquare/wall-oss-0.5-report.txt) §3.1.1）。
- **子任务切分**：长遥操轨迹切成时间连贯的子轨迹，每段对应一个原子子目标并配指令。无本体数据额外标操作对象与关键帧（XRZero-G0 §3.2 第 4 步）。产品版用多模态基础模型做动作切分与语义标注（QUANXTA Zero 第 2 阶段）。
- **仿真数据**：Task DAG 谓词自动给帧级子任务标签（§3.4）。
- **具身桥接样本**：从动作预训练语料自动合成 1,200 万条多模态样本，分四层：物体理解（定位、指点、2D 轨迹预测、属性 VQA）、空间理解（物体关系、多视角指点）、场景理解（场景描述、场景级 VQA）、任务理解（进度预测、affordance、下一步规划）。坐标统一写成 `<box>` / `<point>` 文本 token（wall-oss-0.5-report §3.2）。这是"从同一批轨迹派生 VLM 监督"的现成配方，我们 [curation-pipeline.md](curation-pipeline.md) §4.1 的分层语言标注可以直接扩展到这一层。

我们 [curation-pipeline.md](curation-pipeline.md) §4.1 已经有任务级 + 子任务级分层标注，和他们对齐。差异在于他们在任务级再分 brief / detailed 两档，并系统性做 LLM 改写。

## 7. 配比与采样

**无本体 ↔ 真机配比律**（XRZero-G0 §5.4，[xrzero-g0-paper.txt](sources/xsquare/xrzero-g0-paper.txt)）：
- **基线**：500 条纯真机遥操。
- **1:1 增强**：500 真机 + 500 无本体。插花入瓶任务上，Wall-OSS 成功率从 50% 升到 75%。结论是无本体数据可以抬高固定真机数据量的上限。
- **10:1 替代**：500 无本体 + 50 真机（总量 550，与基线可比）。叠毛巾 87.5% 和基线相同，拿香蕉 75% 和基线相同。论文称之为 "Few-Shot Physical Anchoring"：真机数据只负责把电机延迟、摩擦、关节限位这类本体特有的物理先验"锚定"住。
- **纯无本体**：抓取任务从 300 条扩到 500 条，成功率线性上升，Wall-OSS 在茄子和香蕉上达到 75%。双臂插花用 2,000 条纯无本体数据，在训练高度 0.4 m 上 70%，未见高度 0.45 m 上 60%。论文的解释是：人背着设备移动带来视角和高度变化，打破了固定基座数据的空间过拟合。
- **成本**：综合设备维护、平台开发和人力，无本体数据成本约为真机遥操的 1/20，所以 10:1 配比约等于省掉 90% 的真机预算。

**跨源采样**（[wall-oss-0.5-report.txt](sources/xsquare/wall-oss-0.5-report.txt) §3.1.3 / §3.2）：
- 采样组按（来源 × 任务标签）划分，组内做幂采样 $w_i = n_i^{0.5}$。每组设上限并迭代重分配，防止大组独占预算。
- 一个 epoch 超过 100 万条轨迹，约 60% 自采、40% 开源。开源保留 10 个子集：RoboMIND v1/v2、AgiBotWorld Beta、RoboCOIN、RoboChallenge、Galaxea Open-World、RealOmin、DROID、BRIDGE v2、Fractal。
- 多模态语料约 9,000 万条（7,800 万开源 + 1,200 万桥接），动作:多模态 batch 比 9:1。

这正好对应我们 CLAUDE.md 决策 7 的"数据配方是版本化一等公民"：自变量把配比做成了带消融的研究问题，而不只是一个 yaml 参数。

**开放资产与口径冲突**（[hf-org-listing.txt](sources/xsquare/hf-org-listing.txt)、[hf-xrzero-g0-3k.txt](sources/xsquare/hf-xrzero-g0-3k.txt)）：

| 资产 | 内容 | license | 备注 |
|---|---|---|---|
| `XRZero-G0-3K` | 视频，10,726 行，34 GB，**无数据卡** | 未标注 ⚠️ | 新闻稿称 G0-Dataset "over 2,000 hours"。34 GB 装不下 2,000 h 三视角视频，按常规码率估算仅约几十小时量级（推断 ⚠️）。开放的应该只是子集，名字里的 "3K" 可能对应 3,000 个任务 |
| `X2Real-Dataset` / `x2real-assets` | 约 300 h 仿真轨迹（LeRobot）+ 资产 CSV | Apache-2.0 | 可直接作 sim 轨回归与 Stage A 素材 |
| `libero_all`、若干 benchmark 集 | LIBERO 全集重打包、内部基准 | 未标注 | — |
| `wall-oss-flow` / `-fast` / `-0.5` | 模型权重 | 仓库 tag 未标注；代码 README 未写 license ⚠️ | 进默认路径前要先核 license（CLAUDE.md 约定） |
| XRZero-G0 代码 | 采集与质检代码 | MIT（README 徽章） | 硬件设计是否完全开源未核 |

## 8. 数字可信度

| 宣称 | 出处 | 属性 | 判断 |
|---|---|---|---|
| 10:1 配比与纯真机持平 | XRZero-G0 §5.4 | 公司自报，基线 500 条，任务 5 个，每格评测次数未披露 | 方向可信，量级只在桌面双臂短任务上成立；长程/接触密集任务未测 |
| 无本体成本 = 遥操 1/20 | XRZero-G0 §5.4 | 自报，成本构成没有拆分 | 与新闻列表里的"降低数采成本 60%"口径不同：后者是"无本体+真机"混合配方在简单任务上的整体成本，前者是单条数据成本。两者都不能直接搬进我们的预算 |
| 有效率 85% | XRZero-G0 §3.2；QUANXTA Zero | 自报，"under controlled experimental settings" | 含人工复核；作为我们 device 轨漏斗的外部参照，不作阈值 |
| 2,000 h G0-Dataset | 论文 + 开源新闻稿 | 自报；开放部分 34 GB | 开放量与宣称量不符（§7） |
| 近 100 条/小时、2.33× | QUANXTA Zero；XRZero-G0 Fig.5 | 自报；2.33× 只是简单任务的倍率 | 中等和困难任务分别只有 1.88× / 1.71× |
| TwinDEX 5.3×、几百条完成后训练 | twindex-launch | 自报（D-03/D-04） | 已降权，理由不变：效率依赖 WALL 基座 |
| sim-real 相关 0.84 | X2Real | 自报，他们自己的本体与任务 | 恰好过我们 U-20 口径（仿真代理与真机 Pearson ≥0.8）的门槛，说明这个目标可达；但只适用于他们的刚体任务，不能当作通用值 |
| 物流 1,816 件/小时、>98% | WRC 新闻稿 | 自报，2026-08-12 直播 | 与数据管线无直接关系 |

## 9. 对本仓库的行动项

按收益/成本排序。全部是"先登记、后落地"，不改动 CLAUDE.md 的贯穿性决策。

1. **curation 加"物理回放门"**（device 轨，门①之后）：按（任务 × 末端档案）分层抽样，在目标本体上开环回放，以任务完成谓词为判据，结果写入 episode 指标表，并用来校准 IK 门的阈值。M1 没有本体，先在 [curation-pipeline.md](curation-pipeline.md) §1.3 记为 H1 待实现。
2. **静止帧帧级处理**：现在 §1.3 只做"段占比降级"。补一条帧级规则：用全局统计归一化后，逐维差值低于阈值的帧做标记或降采样（遵守"清洗是标记不是删除"，在 export 取帧时执行）。阈值走 §7 消融。X2Real 的叠积木对照是支持这条的反面证据。
3. **配比消融模板**：在 mixture-runner（M3）里预置"真机固定 + 无本体 0/1×/10×"三组，以及"总量可比的替代组"。数据阶段 B 的 G2 消融按这个格式出报告。
4. **动作语义约定写进契约**：坐标轴朝向、零旋转定义、夹爪极性（大=开）、6D 旋转。列入 [data-format-contract.md](data-format-contract.md) 0.3 待入项。
5. **具身桥接样本**：把 §4.1 分层标注扩展为从 robot/device 轨派生的四层 VQA（物体/空间/场景/任务进度），坐标 token 化。Stage B 做多模态共训时启用。
6. **人机分流规则**：§9 HITL 补上"按 VLM 置信度分流"的具体路由。阈值以人工复核的抽检结果为准。
7. **sim 轨借鉴 Task-DAG 谓词标注**：sim 轨的子任务边界用成功谓词首次为真的帧自动产生，不再走 VLM 事后切分。写进 sim-track 设计。
8. **竞品提示（产品化）**：QUANXTA Zero 是"采集硬件 + App 任务市场 + 清洗标注质检 + 训练评测"一站式对外销售，和我们路线图的 PL3"策展即服务"（[data-strategy-roadmap.md](data-strategy-roadmap.md)）正面重叠。它的卖点是有效率 85%、隐私脱敏加动态水印。PL3 的差异点需要在 PM 侧重新论证。
9. **外部数据**：`X2Real-Dataset`（Apache-2.0）可进 sim 轨回归集候选。`XRZero-G0-3K` 没有 license 和数据卡，不进默认路径。

## 10. 未核与缺口

- WALL-B 没有技术报告。WUM 架构、训练数据小时数、"数百志愿者家庭"都只有媒体转述 ⚠️。
- QUANXTA Zero 产品页（x2robot.com/pages/quanxtazero）和官网新闻详情页都是 SPA，curl 只拿到空壳。新闻稿走 PR Newswire 的公司原文归档。"降低 60%"只在官网新闻列表标题里出现，正文未抓到。
- HOST、WALL-SS、WALL-WM、X-Tokenizer 的论文本次没有精读，只引用官网时间线的一句话摘要。
- `wall-oss-1.0-lite-robodojo` 与 `robodojo-memory-annotations` 是 2026-10 下旬的新仓库，内容未披露，下次复检时补。
