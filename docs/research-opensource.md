# 开源机器人数据管线生态调研与技术选型（2026-08）

> 调研时间：2026-08-29。原调研 agent 中途挂起，本报告由其已完成的 13 组检索结果综合而成；个别未覆盖点标注"未及查证"。选型建议针对本仓库目标：对标 Figure（Helix 02 + Figure 03 + Index）的开源数据管线。

---

## 1. 数据集格式

### LeRobotDataset v3.0 —— ✅ 选定为训练侧标准格式

来源：[官方博客](https://huggingface.co/blog/lerobot-datasets-v3)、[v3 文档](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)、[迁移指南](https://huggingface.co/docs/lerobot/en/porting_datasets_v3)

- 表格数据（关节状态、动作、时间戳等低维高频信号）存 **Apache Parquet**；视觉数据合并存 **MP4**（同 episode 帧成组、按相机分 shard）。
- v3 核心改进：**多 episode 打包进单文件**（v2.x 每 episode 一文件，百万级 episode 会崩），用关系型元数据索引；元数据统一进 parquet（不再散落 JSON）；**原生流式加载**（不必全量下载）。
- 自 `lerobot >= 0.4.0` 起内置；当前 lerobot 最新版 **0.6.1**（2026-08-03，[PyPI](https://pypi.org/project/lerobot/)）。
- 另有独立包 **`lerobot-dataset`**（2026-03 起，[PyPI](https://pypi.org/project/lerobot-dataset/)）：松依赖的 LeRobotDataset 独立发行版，适合不想引入整个 lerobot 的集成场景——**适合我们**。

### 对比结论

| 格式 | 采用度 | 优 | 劣 | 我们的用法 |
|---|---|---|---|---|
| LeRobotDataset v3 | HF 社区标准，增长最快 | parquet+mp4 高效、流式、生态工具全 | 高频多模态原始采集不友好 | **训练/发布层标准** |
| RLDS/TFRecord（[OXE](https://arxiv.org/abs/2310.08864)） | OpenVLA/RT-X 预训练标准 | 跨具身规范严谨 | TF 技术栈老化、protobuf 笨重 | 仅做导入兼容 |
| HDF5（ALOHA/robomimic 风格） | 存量大 | 简单直读 | 单文件 episode 不可扩展 | 仅做导入兼容 |
| MCAP（[Foxglove](https://foxglove.dev/product/mcap)） | ROS 2 事实日志标准 | append-only 高压写入耐崩、序列化无关、chunk+checksum+压缩 | 非训练格式 | **采集/机上记录层标准** |

**关键架构决策**：采集层用 **MCAP**（对标 Figure 的机上记录：append-only 抗断电、多流单文件、任意消息 schema），入湖后转换为 **LeRobotDataset v3**（训练消费）。转换工具生态已成熟：[forge](https://github.com/arpitg1304/forge)（RLDS/LeRobot v2/v3/Zarr/HDF5/Rosbag 互转）、`lerobot convert --from-hdf5`、[ALOHADataConverter](https://github.com/muhamuttaqien/ALOHADataConverter)（→LeRobot/GR00T 格式）。

---

## 2. 遥操作采集方案

来源：[GELLO](https://arxiv.org/abs/2309.13037)、[OPEN TEACH](https://arxiv.org/abs/2403.07870)、[Open-TeleVision](https://arxiv.org/pdf/2407.01512)、[Quest2ROS2](https://arxiv.org/html/2601.18289v1)、[Phone2Act](https://arxiv.org/pdf/2605.01948)、[Echo](https://arxiv.org/pdf/2504.07939)、[Humanoid-Teleoperation (IROS 2025)](https://github.com/YanjieZe/Humanoid-Teleoperation)、[USC Humanoid-Teleop](https://github.com/USC-GVL/Humanoid-Teleop)、[ARMADA (Apple)](https://machinelearning.apple.com/research/armada-augmented-reality)

| 方案 | 成本 | 形态 | 适用 |
|---|---|---|---|
| GELLO | <$300 | 3D 打印同构主从臂（Franka/UR5/xArm），全开源 CAD+固件+ROS | 桌面机械臂，精度高 |
| OPEN TEACH | ~$500 (Quest 3) | VR 手势追踪，90 Hz 反馈，38 任务验证，优于 AnyTeleop | 多指手/双臂，低成本 |
| Open-TeleVision | $3,499 | 端到端 ee 映射 + 第一视角回传 | 人形上半身 |
| Apple Vision Pro 方案 | ~$3,500 | 手/腕/头位姿精确追踪（Fourier GR1、Unitree G1 等人形已有开源管线） | 人形全上半身，对标 Figure 35-DoF 最近 |
| Echo | 低 | 主从 + **力反馈** | 需要力觉数据的任务 |
| Phone2Act | 极低 | 手机做硬件无关遥操作 | 规模化众包采集 |

**选型**：以 **Quest 3 手追（OPEN TEACH 路线）为默认遥操作端**（成本/开源度最优），接口抽象成 `Teleoperator` 协议以便接入 AVP/GELLO；人形全身场景参考 USC/YanjieZe 的 AVP 人形管线。值得抄的细节：[episode 级质量评估+实时反馈给操作员](https://arxiv.org/pdf/2605.26349)（采集时即时质控，Closing the Loop 论文）。

### DROID 的规模化采集经验

[DROID](https://arxiv.org/abs/2403.12945)：76k 轨迹/350 小时/564 场景/84 任务/50 采集员/13 机构/12 个月。核心教训：**标准化的可复制采集平台**（统一硬件清单 + 一键部署 + 全车队远程更新）是分布式采集的前提——这正是 Index"官方录制设备 + App"策略的学术版印证。

---

## 3. 数据可视化与 QC

- **rerun**（[rerun-sdk 0.34.1](https://pypi.org/project/rerun-sdk/)，2026-07）：多速率多模态同步可视化，**内置 LeRobotDataset 导入器**（指向目录即可加载），HF 官方数据集可视化 Space 也基于它。→ **选定**为 episode 检视/QC 工具。
- **Foxglove**：2026-08-18 起转型 "physical AI 的 agentic 数据平台"（自然语言查询录制数据）；MCAP 生态的官方查看器。→ 采集侧（MCAP）调试用。

---

## 4. 视频编码

来源：[LeRobot 视频基准](https://github.com/huggingface/blog/blob/main/video-encoding.md)、[AV1 for robotics](https://huggingface.co/blog/haixuantao/av1-for-ai-and-robotics)、[LeRobot v0.6.0 发布说明](https://huggingface.co/blog/lerobot-release-v060)

- 候选编码：h264 / h265 / **AV1**（libsvtav1）。解码侧 **torchcodec** 全面优于 PyAV（MSE/PSNR/SSIM 全胜）。
- 坑：AV1 软件编码慢（~5× 于图像加载）；`yuv444p` 像素格式浏览器不支持（可视化会失败）→ 用 `yuv420p`。
- LeRobot v0.6.0 已暴露完整编码面（codec/quality/pix_fmt/GOP/preset）并**自动检测硬件编码器**（NVENC/VideoToolbox/VAAPI/QSV），软件 AV1 兜底。
- **选型**：入湖转码默认 AV1 (svt-av1, yuv420p, 硬编优先)，机上采集为降 CPU 负载可先 h264 硬编、入湖再转。

---

## 5. 语言指令自动标注

来源：[DeMiAn](https://arxiv.org/html/2605.17077)、[NILS](https://arxiv.org/pdf/2410.17772)、[VLA 数据引擎综述](https://arxiv.org/pdf/2604.23001)

- **DeMiAn**：VLM 按四个维度（物理运动/场景构成/臂位姿/片段级推理）密集重标注演示片段；单次 VLM 调用秒级、亚分钱成本——重标注旧数据比采新数据便宜几个数量级。
- **NILS**：冻结基础模型集成，对未策划长时程演示做**切分+标注**零人工。
- 业界实践：Qwen3-VL-235B-A22B 用于任务/子任务指令精标；标注以 JSON 存储。
- 与 Figure 的 auto-labeling VLM（"你会给机器人什么指令"事后反推）同路线。**选型**：VLM 标注器抽象成接口，默认 Qwen-VL 系（本地）+ Claude API（云端）双后端；输出任务级 + 子任务级两层指令（对齐 Index 的"分层 caption"）。

---

## 6. 仿真数据轨道

来源：[Isaac Lab + GR00T 工作流](https://blog.pebblous.ai/project/AgenticAI/isaac-groot/en/)、[Isaac Lab RL post-training](https://isaac-sim.github.io/IsaacLab/develop/source/experimental-features/rlinf_vla_posttraining.html)、[Isaac-GR00T N1.7](https://github.com/Nvidia/Isaac-GR00T)

- GR00T N1 **数据金字塔**：web 视频 → 合成轨迹 → 真机数据。实测配比：**88 小时真机 + 780K 合成轨迹（≈6,500 小时，11 计算小时生成）**，合成占 ~98%。
- 四阶段管线：Teleop → MimicGen（演示增殖）→ Neural Trajectory → Fine-tune。
- Isaac Lab 已支持对 VLA（GR00T/OpenVLA）做 **RL post-training**（RLinf 实验特性）；Isaac Lab-Arena 做仿真中的策略批量评测。
- **启示**：我们管线的第三条 ingest 轨道（仿真）直接对接 Isaac Lab/MimicGen 产物；评测环节用仿真 Arena 跑回归。

---

## 7. 选型汇总（本仓库技术栈）

| 层 | 选择 | 理由 |
|---|---|---|
| 机上采集/记录 | **MCAP**（Python SDK） | append-only 耐崩、多流单文件、ROS 2 事实标准 |
| 训练/发布格式 | **LeRobotDataset v3**（`lerobot-dataset` 独立包） | 社区标准、流式、parquet+mp4 |
| 遥操作 | Quest 3 手追（OPEN TEACH 路线），接口留 AVP/GELLO | 成本/开源度/人形适配平衡 |
| 可视化/QC | **rerun-sdk**（内置 LeRobot 导入器）+ Foxglove（MCAP 调试） | 双层各用其长 |
| 视频编码 | AV1 (svt-av1/硬编, yuv420p)，解码 torchcodec | LeRobot 官方基准结论 |
| 语言标注 | VLM 自动标注（Qwen-VL / Claude 双后端），分层指令 | DeMiAn/NILS/Figure 同路线 |
| 仿真轨道 | Isaac Lab / MimicGen 产物导入 + Arena 评测 | GR00T 数据金字塔验证 |
| 格式互转 | forge + lerobot convert | 覆盖 RLDS/HDF5/Rosbag 存量 |

未及查证：MuJoCo 侧（非 Isaac）仿真数据生成现状、mcap Python SDK 具体版本号、`lerobot-dataset` 包的精确 API 面——搭骨架时以实际安装为准。
