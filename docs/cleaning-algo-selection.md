# 清洗与标定的开源算法选型论证（传统 vs AI）

> 2026-08-29。承接 [curation-pipeline.md](curation-pipeline.md)，对每个环节给出候选、论证与结论。license 面向"内部数据处理 + 未来可能商用"审查：服务端自用不分发时 GPL 可用但有远期风险，优先 Apache/MIT/BSD。标注"⚠️待核查"的 license 使用前必须确认。

## 0. 总纲：级联过滤 + 三条论证原则

**成本金字塔**（每层淘汰后才进下一层，单位成本差 1–2 个数量级）：

```
第1层 规则/传统 CV     全量, CPU, ~0 成本    （ffprobe、直方图、Laplacian、IMU 积分）
第2层 轻量专用模型     全量, GPU 批处理      （检测器、轻 CNN）
第3层 重模型          通过者/抽样           （SLAM、手部姿态、光流、embedding）
第4层 VLM             抽样/仲裁            （语义审计、标注、分歧仲裁）
```

三条论证原则：

1. **传统方法优先的场景**：判据物理明确（曝光=直方图、抖动=IMU 积分、时间=校验规则）。传统方法可解释、阈值直观、无模型漂移、CPU 全量跑得起。**AI 在这些场景不是更准，只是更贵**。
2. **AI 必须上的场景**：判据是语义的（是不是目标任务、摆拍、手在不在画面、人脸在哪）。传统 CV 在开放环境做语义判断的误报率不可接受。
3. **合规场景用最强模型不省钱**：隐私脱敏漏检一张脸的代价是法律风险，这里的选型标准是召回率不是成本。

---

## 1. 逐环节论证

### 1.1 技术门 —— 纯传统，无争议

ffprobe（LGPL/GPL，进程调用无传染）、MCAP checksum、自写时间戳规则。**结论：无 AI 必要。**

### 1.2 视觉质量门 —— 传统全量 + 许可安全的学习模型抽样

| 候选 | 类型 | license | 评价 |
|---|---|---|---|
| Laplacian 方差 + 曝光直方图 + 块效应（FFmpeg blockdetect） | 传统 | 自写/LGPL | 快、可解释，抓"技术性坏" |
| BRISQUE/NIQE（pyiqa 实现） | 传统学习 | **pyiqa 非商用** ⚠️ | 用 OpenCV 自带 BRISQUE 替代实现可绕开 |
| [FAST-VQA / DOVER](https://github.com/VQAssessment/FAST-VQA-and-FasterVQA) | AI | **非商用研究许可** ⚠️ | 训练于 UGC 美学评价，与"训练数据可用性"目标**错位** |
| Google UVQ / CAMBI（libvmaf） | AI/传统 | Apache-2.0 / BSD | 商用安全 |

**论证**：学习型 VQA 的训练目标是"人觉得视频好不好看"，我们要的是"数据对策略训练有没有用"——美学分高的运镜华丽视频可能恰恰是坏样本。加上 license 非商用，**DOVER 类不进主管线**。
**结论**：第 1 层传统指标全量；UVQ 抽样复核；真正的"可用性"判断交给 1.5 的 VLM 和下游消融。

### 1.3 抖动 —— 传统完胜

IMU 角速度积分（有 IMU 的轨）为主，稀疏 LK 光流（OpenCV，传统）为纯视频兜底。稠密学习光流用在这里是浪费（见 1.8）。**结论：传统。**

### 1.4 隐私脱敏 —— AI，用最强专用模型

**[EgoBlur](https://github.com/facebookresearch/EgoBlur)（Meta，Apache-2.0）**：人脸+车牌检测模糊，Faster-RCNN + ResNeXt（~104M 参数），**专为 Aria 头戴视角训练**（鱼眼畸变、运动模糊、离轴人脸正是它的训练分布），Gen 2 版明确面向头戴设备生态。
**论证**：这是合规义务（原则 3）；传统 Haar/HOG 人脸检测在第一视角场景召回率不可接受；EgoBlur 与我们的设备形态完美对口且许可宽松，没有第二选择的必要。**结论：EgoBlur，全量，第 2 层。**

### 1.5 语义门 + 标注 —— VLM，开源权重优先

**Qwen 系 VL（多数尺寸 Apache-2.0）本地部署**承担全量抽检与三级 caption；商业 API（Claude）做双模型交叉与分歧仲裁。
**论证**：语义判断无传统替代（原则 2）；本地开源权重控制单位成本（DeMiAn 实测单次调用亚分钱级），API 只花在分歧样本上。学术印证：业界用 Qwen-VL 大杯做机器人视频任务/子任务精标。**结论：本地 Qwen-VL 主力 + API 仲裁，第 4 层。**

### 1.6 手部检测与可见率 —— 轻 AI 全量、重 AI 后置

- 全量可见率统计：**MediaPipe Hands**（Apache-2.0）级轻检测器，逐秒采样，GPU 上近乎免费
- 精细关键点（伪标签阶段才跑）：HaMeR（MIT ⚠️待核查）/ WiLoR（**疑非商用** ⚠️）；世界系轨迹线 **HaWoR**/Dyn-HaMR（⚠️待核查）——通义 Egocentric 管线实战选型为 HaWoR（双手腕 6D + MANO 45）+ **MegaSAM**（世界系相机位姿）+ **MoGe-2**（稠密深度），且"静态相机跳过 SLAM 置 identity"省算力，见 [research-qwen-robotics.md](research-qwen-robotics.md) §1
**论证**：可见率是个检测问题不是姿态问题，用姿态模型做门控是十倍浪费；姿态重模型只对过门数据跑（级联原则）。**结论：分层。**

### 1.7 SLAM/VIO 与设备标定 —— 传统为主、学习型补弱纹理

| 用途 | 首选 | license | 论证 |
|---|---|---|---|
| device 轨位姿（UMI 原配） | ORB-SLAM3 | **GPLv3** ⚠️ | 成熟、CPU 实时、UMI 生态默认；服务端自用不分发合规，但远期商用发行有传染风险 |
| GPL 规避备选 | Basalt（VIO） | BSD | 精度接近，社区小些 |
| human 轨弱纹理补强 | [MASt3R-SLAM](https://opencv.org/mast3r-slam/)（~15fps 稠密）/ DPVO / DROID-SLAM | ⚠️逐个核查 | 学习先验对白墙/玻璃等 ORB 必挂场景显著更稳，GPU 成本高 → 只对传统 SLAM 跟丢的 episode 重跑 |
| **相机内参标定（自有设备）** | OpenCV ChArUco | Apache | 无 AI 必要 |
| **相机-IMU 外参 + 时间偏移** | Kalibr | BSD | 事实标准；这是设备出厂标定的核心工序 |
| **标定从视频估计（手机/众包视频，无标定文件）** | GeoCalib（静态相机，单图估畸变+焦距）/ DroidCalib（运动相机，多视图自标定） | ⚠️逐个核查 | 众包视频没有出厂标定，只能从内容估计；通义 Egocentric 管线实战验证的组合（先 Farneback 光流判定相机动/静再分流）；P0 手机方案直接依赖此路线 |

**论证**：位姿估计是几何问题，传统方法在纹理充分时精度/成本双优；学习型的价值是鲁棒性，按"失败重跑"策略使用把 GPU 成本限制在坏样本上。标定纯几何优化，AI 无角色。**结论：传统主干 + 学习型兜底。**

### 1.8 光流与深度（伪标签中间表征）—— AI

- 光流：**RAFT（BSD）** 或其加速版 SEA-RAFT——SOF 证据链就建在学习光流上，传统 Farneback 质量不够
- 单目深度：Depth Anything 系（**小/中杯 Apache，大杯疑 CC-BY-NC** ⚠️）
**结论：AI，第 3 层，只对进入伪标签工厂的数据跑。**

### 1.9 去重/再平衡 embedding —— AI，license 决定选型

候选：InternVideo2 / VideoMAE V2（⚠️逐个核查，部分权重非商用）；**SigLIP 帧特征聚合（Apache-2.0）为商用安全兜底**。
**论证**：去重是语义相似问题（原则 2）；视频原生模型效果更好但 license 混乱，SigLIP 聚合在"近重复检测"上已够用，语义级重复反正只降权不删。**结论：SigLIP 起步，license 核查通过后升级视频模型。**

### 1.10 子任务分割 —— 传统信号优先、AI 兜底

优先级（curation-pipeline §3.2 的论证补全）：夹爪开合沿/接触力（**纯信号处理，传统**）→ 手-物接触（MediaPipe + Grounding DINO（Apache）/SAM2（Apache-2.0））→ 速度极小值（传统）→ VLM 时序定位（贵，做语义合并）。PySceneDetect 类镜头切分工具**不适用**——我们切的是动作单元不是镜头。
**结论：物理事件是最干净的边界（传统），AI 只做人类轨的接触推断与语义命名。**

### 1.11 欺诈检测 —— 传统规则 + embedding 复用

pHash/videohash（传统感知哈希抓完全重复上传）、设备指纹与时空一致性（规则）、跨账户碰撞复用 1.9 的 embedding、屏幕翻拍摩尔纹（轻 CNN，自训，第 2 层）。**结论：以传统与规则为主，AI 仅翻拍检测。**

---

## 2. 汇总表

| 环节 | 结论 | 关键选型 | 层 |
|---|---|---|---|
| 技术门 | 传统 | ffprobe + 自写规则 | 1 |
| 视觉质量 | 传统为主 | Laplacian/直方图 + UVQ 抽样（避开 DOVER 许可） | 1–2 |
| 抖动 | 传统 | IMU 积分 / LK 光流 | 1 |
| 隐私 | AI | EgoBlur（Apache，头戴特化） | 2 |
| 语义/标注 | AI | Qwen-VL 本地 + API 仲裁 | 4 |
| 手部 | 分层 | MediaPipe 门控 → HaMeR 类精标 | 2→3 |
| SLAM/标定 | 传统主干 | ORB-SLAM3/Basalt + Kalibr；MASt3R-SLAM 兜底 | 3 |
| 光流/深度 | AI | RAFT/SEA-RAFT + Depth Anything | 3 |
| 去重 | AI | SigLIP 聚合起步 | 3 |
| 分割 | 传统优先 | 硬件事件锚点 + VLM 语义合并 | 1→4 |
| 欺诈 | 传统为主 | pHash/规则 + 摩尔纹轻 CNN | 1–2 |

**三条全局纪律**：(1) 每个模型的版本与权重哈希进 lineage——模型升级=数据世代切换，必须可追溯；(2) ⚠️项在 M0 结束前完成 license 终审，非商用许可的模型只允许出现在研究分支；(3) 所有 AI 判定阈值与传统阈值一样服从消融裁决（curation-pipeline §7）。
