# 阿里通义机器人栈调研（QwenRobot-Manip / Qwen-VLA / QwenRobot-Nav）

> 来源：阿里云通义线下技术分享现场拍摄 slide（分享时间约 2026-09-02，用户提供照片，2026-09-04 整理）。**非公开发布材料，数字与命名以其正式发布为准**。重要背景：其数据管线与 [research-vla-pretraining.md](research-vla-pretraining.md) §1 引用的 Ego2Robot（arXiv 2026-08）为同一团队同一工作——slide 数字（1,933h、15 本体、Qwen3.5-4B+DiT）与论文吻合且更新。

## 1. Egocentric 数据处理管线：从原始视频到 LeRobot 数据集（对我们最有价值）

四阶段全算子清单（含算力标注），与本仓库伪标签工厂逐环节对照：

| 阶段 | 通义方案（算子 + CPU/GPU） | 对应我们的设计 |
|---|---|---|
| **① 内参估计与畸变矫正** | 长视频切分 20s+2s 重叠、ffmpeg 抽关键帧（CPU）→ Farneback 背景光流判定相机动/静（CPU）→ 动：**DroidCalib** 多视图运动自标定焦距（GPU）/ 静：**GeoCalib** 单图估径向畸变+焦距（CPU）→ 去畸变到标准针孔模型（CPU）→ **MoGe-2** 稠密深度+针孔焦距先验（GPU） | **补齐了我们的盲区**：众包/手机视频没有出厂标定文件，标定必须从视频本身估计——cleaning-algo-selection §1.7 原只覆盖自有设备（ChArUco/Kalibr），需增补此路线 |
| **② 3D 重建与位姿追踪** | 并行两支：A. **HaWoR** 双手 3D 重建→相机系手部 Pose（腕 6D + MANO 45）；B. MoGe-2 深度→**MegaSAM** SLAM→世界系相机位姿（静态相机跳过=identity）→ 汇合：相机系→世界系轨迹（CPU）→ SE3 对齐、**Savgol 平滑**、离群清洗、片段重组（CPU） | 与我们伪标签工厂 §4.2 同构；HaWoR（我们手部方案候选之一）与 MegaSAM 是具体选型答案；"静态相机跳过 SLAM" 是省算力的好细节 |
| **③ 原子动作分割** | 世界系**手腕移动速度→速度极小值点（Local Minima）→ 双手各自切分**原子动作（全 CPU）；输出 104D 状态 / 102D 动作（双手 MANO） | **验证了我们"速度极小值分割"路线**（curation-pipeline §3.2 第 3 条）——且他们把它当主方法而非兜底，VLM 完全不参与切边界 |
| **④ 语言标注与导出** | 每段均匀采样帧→**手腕轨迹投影叠加到采样帧**→Qwen-VL 视觉语言标注→生成双手命令式指令（VLM）→聚合导出 **LeRobot v3.0** + meta 校验 | 与我们方案一致；"轨迹投影叠加再喂 VLM" 是提升标注质量的可抄技巧（VLM 看得见运动轨迹而非只看帧） |

## 2. 训练数据处理"双管线"设计

- **数据预处理管线（human→robot 合成）六步**：Input → Retarget & Smooth → Arm Segmentation → **Hand Removal**（视频里把人手擦除）→ Base Search + IK → **Depth Composite**（把机器人臂合成进原视频）。产出规模（slide 口径，较论文更新）：**1,933h 人类视频 → 15 本体 24,808h 演示；"零专有采集成本实现 38K 小时跨构型数据扩展"**。
- **数据清洗管线**：
  - 针对 Action（State-Action 数值与运动学校验，五阶段）：噪声移除、极值检测、修复时序错位、坐标系对齐、运动学一致校验；
  - 针对 Video（视觉-语言层三阶段过滤）：**指令-动作一致性检查、视频-状态一致性检查**、视频质量检查。
- 对我们的增量：前者与 L1/L2 吻合；后者的两个"跨模态一致性检查"（指令↔动作、视频↔状态）是我们 curation-pipeline 缺失的门类，值得补。

## 3. QwenRobot-Manip：三维对齐与统一架构

Qwen3.5-4B VLM 主干 + flow-matching DiT 动作头，端到端动作轨迹。三个"对齐"设计：

1. **表征对齐**：所有机器人状态/动作映射到统一 **80 维向量**（覆盖单臂/双臂/灵巧手/移动底座配置），输入输出加**二值掩码**保证梯度只流过有效维度——不同构型无冲突共享参数。（动作空间统一的第四方案，介于 π0 零填充与 RDT 128 槽位之间，掩码机制同 RDT）
2. **操作状态对齐**：末端动作以**增量形式表达在相机坐标系**下——视觉上相似的动作在不同构型间数值相近；相机外参通过注意力层 **CaPE** 注入、内参直接编码进视觉 token（感知视场角）。
3. **跨本体/上下文对齐**：结构化**具身感知提示**（机器人平台、执行速度、帧率）+ 历史观测-动作块预测当前动作。

## 4. Qwen-VLA 与 GTA-VLA

- **Qwen-VLA**：操作 VLA + 导航 VLN + 视觉理解统一进共享动作/轨迹空间；**embodiment-aware prompt conditioning** 模板（可直接抄）：`The robot is {robot_tag} with {single arm / dual arms}[, waist][, and mobile base]. The control frequency is {FPS} Hz. Please predict the next {chunk_size} control actions to execute the following task: {ori_instruction}.`；四阶段渐进式训练；DOMINO 基准 OOD 成功率 26.6% 超主流专家模型。
- **GTA-VLA（ECCV 2026）**："Guide, Think, Act"——动作前先出**视觉提示**（框/点）做 grounding，解决直接 sense-to-act 的错定位问题；含歧义目标的人机交互澄清。

## 5. QwenRobot-Nav

- Qwen3-VL 基座的规模化导航模型：**2B–8B 参数一致扩展**；5 大导航域（VLN/ObjNav/Tracking/Driving/EQA）适配；**15.6M 训练样本**跨域训练；轻量 MLP 头输出路径点 (x,y,θ)×8。
- 参数化接口：任务模式 + 可控观测参数（**视觉 token 预算、时间衰减、相机权重、帧采样模式**）——训练时随机化这些参数，推理可任意设置。
- Agent 化设计：上层规划器（Qwen3.7-Plus）做子目标分解/工具调度，Nav 模型作为**智能体可调用的工具**；双级记忆（短期压缩轨迹 + 长期 notebook：已搜索区域/候选物位置/已排除假设）。

## 6. 对本仓库的行动项

1. **标定从视频估计**：cleaning-algo-selection §1.7 增补 GeoCalib（静）/DroidCalib（动）路线，覆盖手机/众包视频无标定文件场景（P0 手机方案直接需要）。✅ 已更新
2. **伪标签工厂算子对表**：HaWoR（手）、MegaSAM（SLAM）、MoGe-2（深度）纳入候选清单（license 待核查）。✅ 已更新
3. **清洗补两个跨模态一致性门**：指令-动作一致性、视频-状态一致性。✅ 已更新 curation-pipeline
4. **标注技巧**：VLM 标注前把手腕轨迹投影叠加到采样帧。✅ 已更新 curation-pipeline
5. 动作空间统一第四方案（80 维+掩码+相机系增量动作）记入预训练调研对照表。
