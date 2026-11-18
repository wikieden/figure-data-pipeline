# 机器人研发工具链调研：中间件、仿真、建模、规划控制、全身控制、部署、数据平台、建图导航与感知（2026-11-05）

> 范围：**研发过程中用到的工具**，补 [research-opensource.md](research-opensource.md)（数据格式 / 遥操作 / 可视化 / 编码 / 标注 / 仿真数据）与 [research-open-ecosystem-2026.md](research-open-ecosystem-2026.md)（数据集 / 基准 / 模型骨架 / 训练框架 / 资源账）没覆盖的部分；两份文档已有的条目这里只写变化。dora-rs 的详细评估见 [research-generalist-dora.md](research-generalist-dora.md)。
>
> 版本与发布日期于 2026-11-05 从 PyPI JSON 接口与 GitHub Releases API 直接取得（下称"PyPI 实测"），同日 23:30 EST 全部复查并更新；没有 release 的仓库写 tag，连 tag 也没有的写最近一次提交日期并注明；§9–§12 的 license 于同日读取各仓库 LICENSE 文件原文核对（下称"LICENSE 原文"），GitHub 只报 `NOASSERTION` 的都逐个读了原文。来源属性：**官方** = 官方仓库 / 文档 / 发布说明；**论文** = arXiv；**第三方** = 媒体、博客、比较站；**自报 ⚠️** = 发布方自己的性能数字，无独立复现。**license 列只写在 PyPI 元数据或官方页面上核到的；写"未核"的，引入前按 [cleaning-algo-selection.md](cleaning-algo-selection.md) 的 license 规则补核。**

## 0. 一句话结论

| 问题 | 结论 |
|---|---|
| 今天最需要处理的变化 | **LeRobot 0.7.0 于 2026-11-05 发布**，破坏性改动多：W&B 换 Trackio、FSDP1 换 FSDP2/HSDP、`async_inference` 移除、Linux 默认 CUDA 13 轮子（驱动 ≥580.65）。我们 [training-pipeline.md](training-pipeline.md) 写的是 `lerobot ≥0.6`，升级前要锁版本并跑一次迁移（§7） |
| 仿真器选哪个 | 物理引擎层在收敛：**Newton**（Linux 基金会，NVIDIA + DeepMind + Disney，1.0 于 2026-03-21 GA，现 1.7.0）把 **MuJoCo Warp** 收作求解器之一；**Isaac Lab 3.0**（2026-10-19 上 PyPI）可以不装 Isaac Sim、直接跑 Newton 后端。我们的 sim 轨默认 **MuJoCo / MJWarp 资产 + Isaac Lab 3.0 任务 API**，两边都能吃同一份 MJCF |
| 人形全身控制有没有现成的 | 有：**NVIDIA GR00T-WholeBodyControl / SONIC**（2026-02-19 放权重、C++ 推理和 VR 遥操作；代码 Apache-2.0，权重 NVIDIA Open Model License），加上 BONES-SEED 动作库（142K+ 条 / ~288 h，带 G1 MuJoCo 轨迹）。训练自己的跟踪策略用 **mjlab**（Apache-2.0，Isaac Lab API + MJWarp）或 Isaac Lab 3.0；动作重定向用 **GMR**（MIT，17 款人形） |
| 中间件 | ROS 2 仍是生态底座（Lyrical 为现行 LTS；Nav2 的 Lyrical 版 1.5.3 已于 2026-10-17 发布），默认 RMW 仍是 Fast DDS，Zenoh 从 Kilted 起是一级可选；`ros2 bag` 自 Iron 起默认写 **MCAP**，和我们的采集格式一致。需要确定性回放的机上图可以看 **Copper-rs**（1.0 于 2026-07-03，现 1.3.1），数据流式管线继续用 dora-rs（1.1.0） |
| 规划 / 动力学 | **cuRoboV2**（论文 2026-03；代码 **v0.9.0 于 2026-11-05 正式发布**，Apache-2.0，API 与 v1 不兼容，新增 C++ 部署、MPC 与带 LiDAR 融合的体素建图）做 GPU 碰撞规避与人形全身 IK；**Pinocchio**（`pin` 4.1.0）+ **Crocoddyl**（3.2.1）做动力学与 MPC；**Drake**（1.58.0）做离线优化与验证 |
| 部署 | Jetson Thor 上 GR00T N1.7 用 NVFP4 混合量化 + TensorRT，端到端 **125 ms → 39.9 ms**（官方教程，自报 ⚠️）；TensorRT Edge-LLM 官方支持 Thor 与 VLA checkpoint，但没列 GR00T |
| 建图与定位 | 机上视觉定位用 **cuVSLAM**（NVIDIA Community License：可商用但**只许在 NVIDIA 平台上用**）或 Basalt（BSD，见 U-10）；三维占据重建用 **nvblox**（Apache-2.0）；激光用 **GLIM** / **KISS-ICP**（均 MIT），FAST-LIO2 / FAST-LIVO2 是 **GPL-2.0**。学习型稠密重建里 **MapAnything 代码 Apache-2.0**、VGGT 只有 `VGGT-1B-Commercial` 权重可商用、**MASt3R-SLAM 是 CC BY-NC-SA**（governance U-11 第 8 项可据此结案） |
| 导航 | 固定场地（洗衣房）用 **Nav2**（Apache-2.0 / 部分 LGPL-2.1）+ 预建地图 + 对接位，不需要学习型导航。学习型导航模型（InternVLA-N1、NavDP、NaVILA）都还停在仿真或研究阶段，**NavDP 仓库没有 LICENSE 文件**，不能用 |
| 分割与识别 | 默认 **SAM 2**（Apache-2.0）+ **Grounded-SAM-2 / Grounding DINO**（Apache-2.0）做开放词汇；SAM 3 / 3.1 能力更强但是 Meta 自定义的 SAM License（可商用、有禁用条款、gated）。实时检测用 **RF-DETR**（Apache-2.0，按 checkpoint 核）或 **D-FINE**（Apache-2.0）；**Ultralytics YOLO 系与 YOLOE 是 AGPL-3.0，DEIMv2 是禁止商用的自定义许可**，三者都不进默认路径 |
| 多模态感知 | 骨干用 **DINOv2**（主模型代码与权重 Apache-2.0；同仓库 XRay-DINO / Cell-DINO 非商用），DINOv3 待 LEGAL；DINO-X / Grounding DINO 1.5 只有云 API。深度：Depth Anything 3 只有 **Small / Base / Metric-Large 是 Apache-2.0**，Large / Giant / Nested 是 CC BY-NC；MoGe 代码 MIT（权重未核）；FoundationStereo 仅限研究。点跟踪 CoTracker 是 **CC BY-NC**。骨干 DINOv3 是 Meta 自定义许可 |
| 数据平台 | 可视化维持 rerun（最新 0.42.0，我们锁在 0.36.3，差 6 个小版本）+ Foxglove（2026-04 加了数据搜索 / 策展与自带存储）；多传感器标注外包候选 Encord / Segments.ai，比较材料多为厂商自写，需试用后再定 |

---

## 1. 中间件与运行时

| 工具 | 最新版本 / 日期 | license | 要点 | 来源属性 |
|---|---|---|---|---|
| [ROS 2 Lyrical Luth](https://docs.ros.org/en/lyrical/Releases/Release-Lyrical-Luth.html) | 已作为 LTS 发布（计划 GA 2026-05-22；一份发布工作组文档写 2026-06-08，日期不一致） | Apache-2.0（核心） | 默认 RMW 仍是 `rmw_fastrtps_cpp`；RMW 功能冻结推迟 1 周。docs.ros.org 对抓取返回拦截页，发布说明正文未核 | 官方文档（发布前版本）+ 社区邮件列表 |
| [rmw_zenoh](https://github.com/ros2/rmw_zenoh) | 随 Kilted 起为一级 RMW | Apache-2.0 | 从 Kilted Kaiju（2025-05）起是一级支持的 RMW，但不是默认；对跨网段、无组播的现场网络（Wi-Fi 遥操作、云端监控）比 DDS 省心 | 官方 |
| [rosbag2 + MCAP](https://discourse.openrobotics.org/t/psa-default-ros-2-bag-storage-format-is-changing-to-mcap-in-iron/28489) | 自 Iron（2023-05）默认 | — | `ros2 bag record` 默认写 MCAP；Humble 及更早要装 `rosbag2_storage_mcap` 并加 `--storage-id mcap`。**意味着 ROS 2 机器人的现成录制直接就是我们 recorder 层的格式**，ingest 只需校验 schema，不需要转码 | 官方论坛 + [Foxglove 博客](https://foxglove.dev/blog/mcap-as-the-ros2-default-bag-format) |
| [mcap](https://pypi.org/project/mcap/)（Python） | 1.6.0 / 2026-10-19 | 未在 PyPI 元数据写明（仓库为 MIT，未核） | 我们 `pyproject.toml` 写 `>=1.4.0`、`uv.lock` 实锁 1.4.0，无已知破坏性改动，可按需升 | PyPI 实测 |
| [dora-rs](https://github.com/dora-rs/dora) | 1.1.0 / 2026-10-08 | MIT | 数据流式框架，Python/Rust 节点、零拷贝共享内存；评估见 [research-generalist-dora.md](research-generalist-dora.md) | PyPI 实测 |
| [Copper-rs](https://github.com/copper-project/copper-rs) | **1.3.1 / 2026-10-23**（GitHub release；crates.io `cu29` 1.3.1 / 2026-10-21）；首个稳定版 1.0 为 2026-07-03 | 未核 | Rust 运行时：任务图在编译期生成时间触发调度器，**同一份日志回放时按同顺序执行同一份代码**（确定性回放）；统一日志记录全部消息 + 周期性状态快照；有 Zenoh 桥接 ROS 2。延迟优势目前只有自家文档与少量第三方文章，[Codethink](https://www.codethink.co.uk/articles/2026/copper-rs-real-time-robotics.html) 也认为还需实测 | 官方文档 + 第三方 |

**对本仓库**：recorder 层不必自己写 ROS 2 适配——机器人侧跑 ROS 2 的，直接收 rosbag2 产出的 MCAP；不跑 ROS 2 的（自研本体、手持设备），用 `mcap` Python SDK 直写。Copper-rs 的"确定性回放"正好对应 [recorder-sync-and-storage.md](recorder-sync-and-storage.md) 里"按日志复现机上行为"的需求，但它要求整张机上图用 Rust 写，迁移成本高，**先记为观察项，不进默认路径**。

## 2. 仿真与物理引擎

| 工具 | 最新版本 / 日期 | license | 要点 | 来源属性 |
|---|---|---|---|---|
| [MuJoCo](https://github.com/google-deepmind/mujoco) / [MJX](https://mujoco.readthedocs.io/en/stable/mjx.html) / [MuJoCo Warp](https://github.com/google-deepmind/mujoco_warp) | 三者同步 3.17.0 / 2026-10-22 | Apache-2.0 | MJWarp 是 NVIDIA Warp 上的 GPU 版 MuJoCo，自 3.3.5 起可作 MJX 后端（`pip install mujoco-mjx[warp]`），同时是 Newton 的求解器之一。CPU 版 MuJoCo 仍是接触精度与可复现性的参照 | PyPI 实测 + 官方文档 |
| [Newton](https://github.com/newton-physics/newton) | 1.0 GA 2026-03-21；现 1.7.0 / 2026-10-14，按月发版 | Apache-2.0 | Linux 基金会项目（2025-09-29 宣布，Disney Research + Google DeepMind + NVIDIA 共建），基于 Warp + OpenUSD。求解器：**MuJoCo Warp**（广义坐标，大规模并行训练）、**Kamino**（Disney，最大坐标，闭链机构如灵巧手 / 腿，beta）、**VBD**（线缆 / 布料 / 体变形）、**隐式 MPM**（颗粒介质）；碰撞支持 CAD 网格 SDF 与 hydroelastic。宣称 MJWarp 比 MJX 在 locomotion 快 252×、manipulation 快 475×（RTX PRO 6000 Blackwell，自报 ⚠️，无基准细节） | 官方公告 + [LF 新闻稿](https://www.linuxfoundation.org/press/linux-foundation-announces-contribution-of-newton-by-disney-research-google-deepmind-and-nvidia-to-accelerate-open-robot-learning) |
| [Isaac Lab 3.0](https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0) | 3.0.0 / PyPI 2026-10-19（Release 页写 10-20） | BSD-3-Clause | **多后端**：物理（Newton / PhysX）、渲染、可视化三者独立选择；多数工作流**不需要安装或启动 Isaac Sim**；统一 `isaaclab` CLI 覆盖 RSL-RL / RL-Games / skrl / SB3 / RLinf / TorchRL；新增面 / 体变形、VBD 与 MPM 耦合、LEAPP 策略导出。目标栈：Isaac Sim 6.2（v6.2.0 于 2026-10-14 发布）、Python 3.12、PyTorch 2.11 + CUDA 13.0、Warp 1.17、Newton 1.6.1。Isaac Sim 仍是 ROS 桥、XR、Kit 工具的完整 PhysX/RTX 路径，但变成可选 | 官方 |
| [Genesis](https://github.com/Genesis-Embodied-AI/Genesis) | `genesis-world` 1.4.5 / 2026-10-22 | 未核（PyPI 元数据为空） | 2024-12 发布时宣称速度极高；[独立测评](https://stoneztao.substack.com/p/the-new-hyped-genesis-simulator-is)称纯物理比 ManiSkill 慢 3–10×，且官方基准用了最快但精度低的求解配置（夹爪里方块掉落）。2026 年未见新的独立基准 | PyPI 实测 + 第三方 |
| [ManiSkill3](https://arxiv.org/abs/2410.00425) | `mani-skill` 3.0.1 / 2026-04-21 | 未核 | PhysX GPU 并行仿真 + 并行渲染，自报带渲染 10–1000× 快于其他平台、显存省 2–3×（自报 ⚠️）；更新节奏明显慢于 Newton / Isaac Lab | 论文（RSS 2025 / ICLR 2025）+ PyPI 实测 |

**判断**：2026 年的仿真栈从"选一个仿真器"变成"选一个任务 API + 选一个物理后端"。Isaac Lab 3.0 的任务 API 已经能挂 Newton（内含 MJWarp），mjlab 则直接用 Isaac Lab 的 manager API 跑 MJWarp（§4）。所以 [sim-track.md](sim-track.md) 的资产应以 **MJCF 为主格式**（MuJoCo / MJWarp / Newton / mjlab 原生可读），需要 RTX 渲染或 Isaac Sim 工具时再转 USD（§3）。Genesis 和 ManiSkill3 不进默认路径：前者精度争议未解，后者更新慢且与 Newton 生态不通。

## 3. 机器人描述与资产转换

| 工具 | 版本 | 要点 | 来源属性 |
|---|---|---|---|
| [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) | 持续更新 | 官方维护的高质量 MJCF 模型库（含 Unitree G1/H1、多种灵巧手），Isaac Lab 的 MJCF 导入示例也用它 | 官方 |
| [mujoco-usd-converter](https://pypi.org/project/mujoco-usd-converter/) | **0.9.0 / 2026-11-05**，仍为 **alpha**（README） | MJCF → OpenUSD，Newton 项目的一部分；Isaac Sim 5.0 起的 MJCF 导入器改用此库 | 官方（PyPI + [Isaac Lab 文档](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta/source/how-to/import_new_asset.html)） |
| [mujoco_ros2_control 的 URDF→MJCF 工具](https://control.ros.org/kilted/doc/mujoco_ros2_control/mujoco_ros2_control/docs/tools.html) | Kilted 文档 | 官方自称"hacky and highly experimental" | 官方 |
| [urdf2any](https://pypi.org/project/urdf2any/) | — | 纯 Python URDF → USD / MJCF，社区包，成熟度未核 | 第三方 |

**坑**：URDF → MJCF 转换丢掉的正是仿真里最影响接触的参数——每个 geom 的摩擦、`solref` / `solimp`、MuJoCo 专有传感器，转换后需要手工补（[第三方](https://simready.artlabs.ai/compare/urdf-vs-mjcf-for-ros-2)）。**建议**：自研本体（[inhouse-isomorphic-end-effector.md](inhouse-isomorphic-end-effector.md) 的手、躯干）以 MJCF 为唯一手写源，URDF 由 MJCF 生成给 ROS 2 / MoveIt 用，而不是反过来；转换脚本和接触参数一起进版本控制。onshape-to-robot（CAD → URDF/MJCF）本次未查到 2026 年状态，未核。

## 4. 人形全身控制、强化学习与动作重定向

| 工具 | 版本 / 日期 | license | 要点 | 来源属性 |
|---|---|---|---|---|
| [GR00T-WholeBodyControl / SONIC](https://github.com/NVlabs/GR00T-WholeBodyControl) | 权重 + C++ 推理 + VR 遥操作 2026-02-19 | 代码 Apache-2.0；**权重 NVIDIA Open Model License**（[模型卡](https://huggingface.co/nvidia/GEAR-SONIC)） | 42M 参数全身控制基础模型，定位"System 1"快速反应控制器，上接慢速规划 / VLA；后续放出 **BONES-SEED**：142K+ 条人体动作 / ~288 h，附 G1 MuJoCo 轨迹。性能结果主要来自仿真，未见规模化真机部署 | 官方 + 第三方 |
| [mjlab](https://github.com/mujocolab/mjlab) | 1.6.0 / 2026-08-09 | Apache-2.0（内含 Isaac Lab 派生工具代码，BSD-3） | Isaac Lab 的 manager-based API + MuJoCo Warp；自带 G1 速度跟踪与动作模仿任务；训练需 NVIDIA GPU，macOS 只能评估；论文 arXiv:2601.22074 | PyPI 实测 + 官方 |
| Isaac Lab 3.0 | 见 §2 | BSD-3-Clause | 统一 CLI 接 RSL-RL（5.5.1）等；LEAPP 策略导出 | 官方 |
| [GMR](https://github.com/YanjieZe/GMR) | 2026-01-21 加 Xsens BVH；2026-01-12 加 Fourier GR3（第 17 款人形） | MIT | 人体动作 → 人形重定向；输入 SMPL-X（AMASS / OMOMO）、BVH（LAFAN1）、FBX（OptiTrack）、GVHMR 视频位姿；论文论证重定向伪影（脚滑、自穿透）直接拖累 RL 跟踪策略 | 官方 + 论文 |
| [dex-retargeting](https://github.com/dexsuite/dex-retargeting) | 0.5.0 / **2025-04-05** | MIT | 灵巧手重定向事实标准，但 **18 个月无新版**，新手型要自己写配置 | PyPI 实测 |

**对本仓库**：
- robot 轨的人形全身遥操作（[robot-track-teleop.md](robot-track-teleop.md)）可以直接评估 SONIC 的 VR 遥操作链路作为下肢 / 全身平衡层，上肢操作仍走我们自己的遥操作。**权重 license 不是 Apache**，商用前须核 NVIDIA Open Model License 条款，先放研究分支。
- human 轨视频经 GVHMR 估位姿 → GMR 重定向，可产出人形可执行的参考动作，是 human→robot 迁移的一条现成工具链；重定向质量本身应作为一道 QC 门（脚滑 / 自穿透可算），对应 [curation-pipeline.md](curation-pipeline.md) 的 L1 运动学过滤。

## 5. 动力学、运动规划与控制

| 工具 | 版本 / 日期 | license | 要点 | 来源属性 |
|---|---|---|---|---|
| [cuRoboV2](https://github.com/NVlabs/curobo) | **v0.9.0 / 2026-11-05**（GitHub release，首个 V2 正式版）；论文 2026-03-05（[arXiv:2603.05493](https://arxiv.org/abs/2603.05493)） | Apache-2.0 | 重写版：B 样条轨迹优化（平滑 + 力矩限）、GPU TSDF/ESDF 感知、高自由度全身计算（含可微逆动力学）。自报 3 kg 负载下成功率 99.7%（基线 72–77%）、48 自由度人形无碰撞 IK 99.6%（自报 ⚠️）。**API 与 v1 不兼容**，依赖 v1 的要锁 `v0.7.8` 标签。v0.9.0 发布说明另列：GPU 双向 RRT + 定路径 TimeOpt、笛卡尔路点规划、**C++ 部署（规划 / MPC / 建图，可跨 GPU 导出）与机器人位姿标定**、体素建图加 RGB / 特征融合与**语义查询、LiDAR 接入**。注意 PyPI 上的 `curobo` 包（0.2 / 2024-01）不是官方发行，安装走仓库 | 论文 + 官方仓库 |
| [Pinocchio](https://github.com/stack-of-tasks/pinocchio)（`pin`） | 4.1.0 / 2026-07-08 | BSD-3-Clause | 刚体动力学与解析导数，人形 MPC / 逆动力学的底座 | PyPI 实测 |
| [Crocoddyl](https://github.com/loco-3d/crocoddyl) | 3.2.1 / 2026-05-21 | BSD-3-Clause | 基于 Pinocchio 的 DDP 最优控制 / MPC 求解器，在 Talos 等力矩控制人形上验证过 | PyPI 实测 + 论文 |
| [Drake](https://github.com/RobotLocomotion/drake) | 1.58.0 / 2026-10-15 | BSD-3（含多种依赖许可） | 轨迹优化、接触仿真、形式化验证；适合离线分析，不适合高并行 RL | PyPI 实测 |
| MoveIt 2 | 随 ROS 2 发版 | BSD-3 | 机械臂规划的 ROS 2 标准；cuRobo 可作其 GPU 规划插件（NVIDIA cuMotion） | 官方（本次未单独核版本） |

**对本仓库**：这一层主要服务两件事。一是**数据回放校验**——用 Pinocchio 对遥操作录到的关节轨迹算力矩、检查是否超限，是 L1 运动学过滤里比"关节越限"更强的一道门（[curation-pipeline.md](curation-pipeline.md)）。二是**仿真数据增殖**——cuRoboV2 的无碰撞全身 IK 可以给 sim 轨生成大量合法的人形到达 / 抓取轨迹。

## 6. 部署与推理

| 工具 / 路径 | 要点 | 来源属性 |
|---|---|---|
| [GR00T N1.7 on Jetson Thor](https://www.jetson-ai-lab.com/tutorials/groot_n17_on_thor/) | 每个子模块导出 ONNX → 校准 → 建 TensorRT 引擎，NVFP4 混合量化；端到端 **125 ms → 39.9 ms（3.1×）、25 Hz，任务成功率无可测损失**；JetPack 7.2、MAXN 模式。上游 Isaac-GR00T 仓库不含这些优化，教程在锁定 commit 上打补丁 | 官方教程（自报 ⚠️） |
| [TensorRT Edge-LLM](https://nvidia.github.io/TensorRT-Edge-LLM/0.11.1/overview.html) | 0.11.1（GitHub release 2026-10-28），官方支持 AGX Thor，支持 VLA checkpoint（示例为 Alpamayo、Cosmos 等，**未列 GR00T**）；I/O 不是 LLM 形状的走"模型专用运行时" | 官方文档 |
| Isaac Lab LEAPP 导出 | RL 策略从训练环境直接导出部署格式（3.0 新增，细节未核） | 官方 |
| LeRobot 0.7 `lerobot-policy-server` | 取代被移除的 `async_inference`，`lerobot-rollout --inference.type=remote`（§7） | 官方 |

与 [research-open-ecosystem-2026.md](research-open-ecosystem-2026.md) §5.3 的 VLA-Perf 数字对照：π0 在 Thor 19 Hz（未量化）；GR00T N1.7 NVFP4 后 25 Hz。两者都说明**机上 VLA 推理靠量化 + TensorRT 能进 20 Hz 档，但 100–200 Hz 的 S1 控制回路仍要另起一个小模型**（SONIC 42M 正是这个位置），与 [runtime-and-deployment.md](runtime-and-deployment.md) 的双系统分层一致。

## 7. 训练工具链补遗：LeRobot 0.7.0（2026-11-05）

[发布说明](https://github.com/huggingface/lerobot/releases/tag/v0.7.0)列出的、会影响本仓库的破坏性改动：

| 改动 | 影响 | 动作 |
|---|---|---|
| Linux 上 `torch` / `torchvision` 改为 PyPI 的 CUDA 13 轮子，要求 NVIDIA 驱动 ≥ 580.65；`cu128` 索引取消 | 训练机驱动老的会直接装不上 | 训练机先核驱动版本；老驱动按安装指南先从 CUDA 12 索引装 torch |
| W&B 换成 **Trackio**（`--wandb.*` → `--trackio.*`），检查点默认不再作为 artifact 上传 | 实验追踪与 lineage 记录方式变化 | [training-pipeline.md](training-pipeline.md) 里实验追踪写法要更新；配方哈希入 lineage 不依赖 W&B，影响有限 |
| FSDP1 → **FSDP2 / HSDP**（`--parallelism.dp_shard` / `dp_replicate`）；≤0.6.x 的 FSDP 检查点**不能续训**（权重仍可加载） | Stage B 多机预训练方案（U-44 的 LeRobot 一侧）反而更有利 | 升级前把在训任务跑完，不要跨版本续训 |
| `--policy.use_peft=true` 现在真的训 LoRA（以前会静默全参） | 0.6 时代用这个开关跑出的"LoRA"结果其实是全参微调 | 复查已有实验记录 |
| 批量图像增强里 7 种变换在 uint8 帧上曾是**静默空操作**，现在生效 | 0.6 下开了这些增强的实验等于没开 | 同上，复查；对比实验要标注 lerobot 版本 |
| `lerobot.async_inference` 移除，改用 `lerobot[remote]` + `lerobot-policy-server` | 推理侧接口变化 | 对应 §6 |
| `lerobot.envs.<sim>` → `lerobot.sim.integrations.<sim>`，环境配置改名 `*EnvConfig` | 评测脚本要改 import | 对应 [eval-protocol.md](eval-protocol.md) |

本仓库 `pyproject.toml` 目前没有直接依赖 `lerobot`（只依赖 `mcap` 与 `rerun-sdk`），所以不会被动升级；但引入时应**直接锁 0.7.x**，避免先写 0.6 代码再迁移——前提是 governance R-15 的读侧验证通过（0.7 发布说明的数据集破坏性改动只有流式读取器，v3 磁盘格式未列，但尚未用我们的 `fdp.*` 扩展列验证）。0.7 另外新增了 SONIC 解码器、LanceDB 存储后端与存储后端注册表、Foxglove 回放的非默认后端支持。

## 8. 可视化、可观测与数据平台

| 工具 | 版本 / 动态 | 要点 | 来源属性 |
|---|---|---|---|
| [rerun-sdk](https://pypi.org/project/rerun-sdk/) | 0.42.0 / 2026-11-04 | 我们锁 `>=0.36.3`，差 6 个小版本；rerun 小版本间常有 API 变动，升级前跑 viz 测试。0.30 起有 DataFusion 查询接口（`re_datafusion`），可对录制做 SQL 式查询 | PyPI 实测 + docs.rs |
| [Foxglove](https://foxglove.dev/) | 2025-11 B 轮 4000 万美元（Bessemer 领投）；2026-04 发布 Data Search and Curation 与 Bring Your Own Storage | 从可观测工具扩展为"physical AI 数据平台"；BYOS 意味着数据可以留在自有对象存储，对 [compliance-and-security.md](compliance-and-security.md) 的数据驻留要求友好。定价只在竞品比较页上看到（有免费个人档），未核 | 官方新闻稿（[Business Wire](https://www.businesswire.com/news/home/20251112126106/en/Foxglove-Raises-%2440-Million-Series-B-to-Power-the-Future-of-Physical-AI)） |
| [Encord](https://encord.com/blog/data-labeling-platforms-for-physical-ai) | 2025-06 推出 Physical AI 套件 | 多传感器时间线、LiDAR / 点云；第三方摘要称已原生支持 MCAP / ROSBAG 与客户云存储（未核） | 官方 + 第三方 |
| Segments.ai | — | 比利时公司，多传感器（相机 + 点云）同步标注，LiDAR 场景常被推荐 | 第三方目录 |

**判断**：标注平台的比较材料基本都是厂商自写（Encord、Labellerr 各自的"榜单"都把自己排第一），不能作为选型依据。我们的标注主力是 VLM 事后反推（[research-opensource.md](research-opensource.md) §5），人工标注只做抽检与 L3 审计，**需求是"能直接读 MCAP / LeRobot v3 + 数据不出自有存储"**，按这两条去试用，而不是按功能清单比。

## 9. 建图与定位（SLAM）

已登记在 [cleaning-algo-selection.md](cleaning-algo-selection.md) §1.7 的 ORB-SLAM3 / Basalt / Kalibr 不重复；那里是**离线清洗**用途，这里补**机上实时**与**场地建图**用途。

| 工具 | 类型 | 最新版本 / 日期 | license（LICENSE 原文） | 要点 | 来源属性 |
|---|---|---|---|---|---|
| [cuVSLAM](https://github.com/nvidia-isaac/cuVSLAM)（Isaac ROS Visual SLAM） | 视觉-惯性 SLAM，GPU | cuVSLAM v17.0.1 / 2026-10-13；ROS 封装 `isaac_ros_visual_slam` v5.0-0 / 2026-09-22 | **NVIDIA Community License**：可商用、可发衍生作品，但**只许在 NVIDIA 平台上使用** | Isaac ROS 4.6.0（2026-08-18）起从源码构建 x86_64 与 aarch64；5.0.0（2026-09-21）包名改为 `isaac_ros_cuvslam`。Jetson 机上定位的现成选项 | 官方 |
| [nvblox](https://github.com/nvidia-isaac/nvblox) | GPU 三维占据 / ESDF 重建 | v0.0.10 / 2026-05-07（之后持续提交，最近 2026-10-23） | **Apache-2.0** | 深度图 → TSDF/ESDF，直接给 Nav2 代价地图与 cuRobo 避障用；2026-02-02 更新了开源许可 | 官方 |
| [RTAB-Map](https://github.com/introlab/rtabmap) | RGB-D / 双目 / 激光 图优化 SLAM | 0.24.2 / 2026-10-25 | BSD 风格（原文为 BSD 三条款式） | ROS 2 生态里最成熟的通用建图方案，支持多会话地图合并，适合固定场地反复建图 | 官方 |
| [GLIM](https://github.com/koide3/glim) | 激光-惯性建图，可选 GPU | tag v1.2.2（无 release；最近提交 2026-10-08） | **MIT** | [社区基准](https://discourse.openrobotics.org/t/slam-benchmark-on-livox-mid-360-public-dataset-our-own-uav-flight-data-kiss-icp-dlio-fast-lio2-glim/57912)（2026-09，Livox Mid-360，TIERS 室内）APE RMSE：GLIM 0.040 m、DLIO 0.096 m、FAST-LIO2 0.112 m、KISS-ICP 0.123 m；作者提醒 GLIM 的优势可能依赖小型、易回环的室内空间 | 官方 + 第三方 |
| [KISS-ICP](https://github.com/PRBonn/kiss-icp) | 纯激光里程计 | v1.3.0 / 2026-04-26（PyPI 同） | **MIT** | 无回环、无 IMU；上述基准里最不稳（单序列飙到 0.426 m） | 官方 + 第三方 |
| [FAST-LIO2](https://github.com/hku-mars/FAST_LIO) / [FAST-LIVO2](https://github.com/hku-mars/FAST-LIVO2) | 激光-惯性（-视觉）里程计 | 均无 release / tag；最近提交 2026-10-25 / 2026-03-08 | **GPL-2.0**（README 称商用可另与作者谈许可） | 精度与速度口碑好，但 GPL 与 ORB-SLAM3 同等处理：只能服务端、独立进程（[open-source-strategy.md](open-source-strategy.md)） | 官方 |
| [MapAnything](https://github.com/facebookresearch/map-anything)（Meta） | 前馈式度量三维重建 | v1.1.3 / 2026-07-17 | 代码 **Apache-2.0**；权重 license 未核 | 单个 Transformer 统一十几种重建任务（多视图立体、SfM、配准、深度补全），直接回归度量尺度几何 | 官方 + 论文 |
| [VGGT](https://github.com/facebookresearch/vggt)（Meta） | 前馈式相机 + 深度 + 轨迹 | 无 release / tag；最近提交 2026-05-19 | **VGGT License**（2025-07-29 起代码可商用，军事除外）；**只有 `VGGT-1B-Commercial` 权重可商用**，原权重仍为非商用，需申请 | 一次前向预测数百帧的相机、深度与稠密轨迹 | 官方 README |
| [VGGT-SLAM](https://github.com/MIT-SPARK/VGGT-SLAM) | 基于 VGGT 子图的单目 RGB SLAM | 无 release；最近提交 2026-06-29 | 代码 **BSD-2-Clause**（依赖 VGGT 权重，权重许可另算） | 未标定单目相机即可，在 SL(4) 流形上对齐子图（NeurIPS 2025）；2.0（2026-01 arXiv）去掉 15 自由度漂移、加回环验证 | 官方 + 论文 |
| [MASt3R-SLAM](https://github.com/rmurai0610/MASt3R-SLAM) | 稠密学习型 SLAM | 无 release；最近提交 2025-11-09 | **CC BY-NC-SA 4.0** | governance U-11 第 8 项登记为"⚠️待核查"，**原文核实为非商用**，弱纹理兜底在默认路径上要换（VGGT-SLAM + 商用权重，或 MapAnything） | LICENSE 原文 |

**对本仓库**：
- **human 轨 / device 轨的离线位姿**：U-11 第 8 项可以结案为"非商用，只进研究分支"；弱纹理兜底的默认候选改为 MapAnything（代码 Apache，权重待核）或 VGGT-SLAM + `VGGT-1B-Commercial`。
- **机上定位**：自研头戴 / 手持设备若用 Jetson，cuVSLAM 是现成方案，但 NVIDIA Community License 绑定 NVIDIA 平台，换芯片就要换算法；非 NVIDIA 平台继续 Basalt（U-10）。
- **场地建图**：洗衣房这类固定场地，部署前用 RTAB-Map 或 GLIM 建一次地图并版本化，作为导航（§10）与 sim 轨场景重建（[sim-track.md](sim-track.md) §2）的共同底图。

## 10. 导航

[robot-track-teleop.md](robot-track-teleop.md) 定了 H0 本体"固定或轮式即可，人形腿部不进本仓库范围"，所以这里的导航只考虑**轮式底盘在固定场地内移动**，和 human 轨头戴视频导出的导航数据（[index-replica-plan.md](index-replica-plan.md) §4 的 SE(2) 速度指令）。

| 工具 | 最新版本 / 日期 | license | 要点 | 来源属性 |
|---|---|---|---|---|
| [Nav2](https://github.com/ros-navigation/navigation2) | **1.5.3 / 2026-10-17**（"Lyrical sync Oct 16"） | 各部分分别为 **Apache-2.0** 或 **LGPL-2.1-or-later**（LICENSE 原文） | ROS 2 导航标准栈：全局 / 局部规划、行为树、代价地图、对接。[Lyrical 版要点](https://discourse.openrobotics.org/t/nav2-lyrical-release-key-features/57666)：新 `nav2_ros_common` 包、RPP 控制器支持 Dynamic Window Pure Pursuit、组合节点内 IPC 零拷贝、文档站重做。Lyrical 版已发布（1.5.x 线） | 官方 |
| Isaac ROS 导航组件 | 见 §9 | cuVSLAM 为 NVIDIA Community License；nvblox Apache-2.0 | cuVSLAM 定位 + nvblox 代价地图接 Nav2，是 Jetson 上的视觉导航组合 | 官方 |
| [InternNav](https://github.com/InternRobotics/InternNav) / InternVLA-N1 | 0.3.1 / 2026-02-11 | 工具箱 **MIT**；InternVLA-N1 权重未核 | 双系统导航：System 2 是微调后的 Qwen2.5-VL，负责在像素上定目标，System 1 负责执行；附 InternData-N1（3k+ 场景、~830k 条 VLN 样本）。人形评测只在仿真（InternUtopia 里的 Unitree H1） | 官方 |
| [NavDP](https://github.com/InternRobotics/NavDP) | 无 release；最近提交 2026-09-07 | **仓库无 LICENSE 文件**（默认保留全部权利），System 1 权重需填表申请 | 扩散式无地图导航策略，纯仿真训练，自称跨具身迁移无需真机数据 | 官方 |
| [NaVILA](https://github.com/AnjieCheng/NaVILA) | 无 release；最近提交 2025-08-20 | **Apache-2.0** | 腿式机器人视觉-语言导航；一年多无更新 | 官方 |
| [Hydra](https://github.com/MIT-SPARK/Hydra)（MIT SPARK） / [ConceptGraphs](https://github.com/concept-graphs/concept-graphs) | Hydra 最近 release v1.0.0 为 2023-06-09，此后只有提交（最近 2026-11-03）/ ConceptGraphs 最近提交 2025-10-16 | **BSD-2-Clause** / **MIT** | 三维场景图：楼层 → 房间 → 物体分层，物体节点带开放词汇特征，可供 VLM / LLM 做"去哪个筐拿衣服"这类语义查询；Hydra 持续维护，ConceptGraphs 已一年无更新。本次未查到 2026 年的新后继工作 | 官方 + 论文 |

**判断**：洗衣房是封闭、布局固定的场地，Nav2 + 预建地图 + 固定对接位（洗衣机、烘干机、折叠台前）已经够用，**学习型导航不进交付路径**。数据层要做的是：底盘的 `cmd_vel` 与定位位姿作为信号流入湖（[data-format-contract.md](data-format-contract.md) 的位姿与定位行已覆盖），导航段在 episode 内打子任务标签，策展时可以把"移动"与"操作"分开采样。InternData-N1 可作为 human 轨导航伪标签的外部对照，引入前核数据 license。

## 11. 多模态感知（深度、三维、点跟踪、视觉骨干）

[cleaning-algo-selection.md](cleaning-algo-selection.md) §1.6 / §1.8 已登记手部关键点（HaMeR / WiLoR / HaWoR）、光流与深度的离线用法，这里补 2026 年的新版本与 license 原文核对结果。

| 工具 | 用途 | license（LICENSE 原文 / 官方 README） | 要点 |
|---|---|---|---|
| [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3)（PyPI `depth-anything-3` 0.1.1 / 2026-03-04；权重已到 1.1 版） | 单目 / 多视图深度、位姿、度量深度 | **按权重分**：DA3-SMALL（0.08B）、DA3-BASE（0.12B）、**DA3METRIC-LARGE（0.35B，度量深度）为 Apache-2.0**；DA3-LARGE、GIANT（1.15B）、NESTED（1.40B）为 **CC BY-NC 4.0** | 第三方站点对 Metric-Large 的许可说法互相矛盾，以官方 README 表为准。与现有登记"Depth Anything 小 / 中杯 Apache、大杯 NC"一致，DA3 多了一个可商用的度量深度权重 |
| [Video Depth Anything](https://github.com/DepthAnything/Video-Depth-Anything) | 视频时序一致深度 | 代码 **Apache-2.0**；各尺寸权重未核 | 适合第一视角视频，避免逐帧深度闪烁 |
| [MoGe](https://github.com/microsoft/MoGe)（含 MoGe-2） | 单目几何（点图 + 度量尺度） | 代码 **MIT**（内含 DINOv2 代码为 Apache-2.0）；权重未核 | governance U-11 第 17 项的 MoGe-2 代码部分可结案，权重仍待核 |
| [FoundationStereo](https://github.com/NVlabs/FoundationStereo) | 双目深度 | NVIDIA 源码许可，"**仅限研究用途**"（原文 3.3 条） | 与 U-11 第 20 项一致，不进默认路径 |
| [CoTracker](https://github.com/facebookresearch/co-tracker)（CoTracker3） | 任意点长时跟踪 | **CC BY-NC 4.0** | 常被用来从人类视频提取物体 / 手部点轨迹做伪动作，但非商用，只能研究分支 |
| [DINOv2](https://github.com/facebookresearch/dinov2) | 通用视觉骨干 | 主模型**代码与权重均 Apache-2.0**（官方 README）；**同仓库的 XRay-DINO 权重、Cell-DINO 代码与权重为 FAIR 非商用许可** | 见下方 DINO 家族小节 |
| [DINOv3](https://github.com/facebookresearch/dinov3) | 通用视觉骨干 | **DINOv3 License**（Meta 自定义，2025-08-19，含禁用条款） | 与 U-11 第 30 项一致；DEIMv2 等下游模型继承此约束 |
| [Open3D](https://github.com/isl-org/Open3D)（0.20.0 / 2026-09-16） | 点云处理 | **MIT** | 点云配准、下采样、可视化的基础库 |
| [MediaPipe](https://github.com/google-ai-edge/mediapipe)（1.2.2 / 2026-11-03） | 轻量手部 / 人体关键点 | **Apache-2.0** | 清洗第 2 层的手部门控（已登记） |

**DINO 家族**（名字相同、来源与许可完全不同，最容易混用）：

| 成员 | 出处 | 是什么 | license | 默认路径 |
|---|---|---|---|---|
| DINO（v1） | Meta | 自监督 ViT 骨干 | Apache-2.0；仓库已归档（2024-07） | 已被 v2 取代 |
| **DINOv2** | Meta | 自监督视觉骨干（ViT-S/B/L/g） | **Apache-2.0**（主模型代码 + 权重）；同仓库 XRay-DINO / Cell-DINO 为 FAIR 非商用 | **可用**，只取主模型权重 |
| DINOv3 | Meta | DINOv2 后继，更大规模、稠密特征更强 | DINOv3 License（Meta 自定义，禁用条款） | 待 LEGAL（U-11 #43） |
| DINO（检测器）/ Grounding DINO | IDEA Research | DETR 系检测器 / 开放词汇检测 | Apache-2.0；2024 年后无更新 | Grounding DINO 可用（§12） |
| Grounding DINO 1.5 / DINO-X | IDEA Research | 更强的开放世界检测 | **只提供云 API**（仓库只有 Apache-2.0 的客户端 SDK，模型不开放） | 不进默认路径：数据要出域，且 API 条款未审 |

DINOv2 在本仓库的用处：一是作为 Apache 许可下的稠密特征骨干，DINOv3 许可没审完之前，凡是下游模型可选骨干的（检测、深度、MoGe 内部本身就带 DINOv2 代码）都优先选 v2；二是作为清洗去重的候选特征——[cleaning-algo-selection.md](cleaning-algo-selection.md) §1.9 现用 SigLIP 帧特征做商用安全兜底，DINOv2 是实例级特征，对"同一场景、同一物体的近重复"通常比图文双塔更敏感，可作为 SigLIP 的对照做一次去重消融（阈值改动按 CLAUDE.md 决策 4 走消融裁决）。

**判断**：默认路径的可商用组合是 **DA3-SMALL / BASE / METRIC-LARGE + MoGe 代码 + DINOv2 + Open3D + MediaPipe**；点跟踪目前没有可商用的强模型，伪动作提取继续走"手部关键点 + 相机位姿"（[curation-pipeline.md](curation-pipeline.md) §4），CoTracker 只作研究对照。触觉、音频等其余模态的工具本次未调研。

## 12. 目标分割与识别

| 工具 | 类型 | 最新版本 / 日期 | license（LICENSE 原文） | 要点 |
|---|---|---|---|---|
| [SAM 2](https://github.com/facebookresearch/sam2) | 图像 / 视频可提示分割 | PyPI `sam2` 1.1.0 / 2024-12-21（仓库无 release，最近提交 2026-05-30） | **Apache-2.0** | 默认路径的分割底座（已登记） |
| [SAM 3](https://github.com/facebookresearch/sam3) / SAM 3.1 | 概念提示的检测 + 分割 + 跟踪统一模型 | PyPI `sam3` 0.1.4 / 2026-05-26（仓库无 release，最近提交 2026-10-23） | **SAM License**（2025-11-19，Meta 自定义）：允许商用、再分发与衍生，禁止军事 / 核 / 间谍 / ITAR 管制用途，权重 gated | 用文字概念（如"白色毛巾"）直接分割视频里所有实例；SAM 3.1 为后续改进权重（第三方称 2026-03-30，未核一手）。与 U-11 第 21 项一致：非 OSI 许可，按条款逐项审 |
| [SAM 3D Objects](https://github.com/facebookresearch/sam-3d-objects) | 单图物体三维重建 | 无 release；最近提交 2026-06-02 | Meta 自定义许可，未逐条核 | 可作 sim 轨物体资产的候选来源，与 SimFoundry 的换件（U-20）一起评估 |
| [Grounding DINO](https://github.com/IDEA-Research/GroundingDINO) / [Grounded-SAM-2](https://github.com/IDEA-Research/Grounded-SAM-2) | 开放词汇检测 + 分割 | Grounding DINO 无 release（最近提交 2024-08-12）/ Grounded-SAM-2 v1.0 / 2024-12-11 | **Apache-2.0** | 文字 → 框 → SAM 2 掩码；Grounding DINO 原仓库 2024-08 后无更新，1.5 / DINO-X 只有 API |
| [RF-DETR](https://github.com/roboflow/rf-detr)（Roboflow） | 实时检测 / 实例分割 | 1.11.2 / 2026-10-04（PyPI 包名 `rfdetr`） | 仓库 **Apache-2.0**；Roboflow 许可页称部分尺寸（Atto / Femto / Pico / XL / 2XL）走其 Platform Model License，**按 checkpoint 核** | GPU 上精度领先、易微调；第三方称无 CPU 实时路径 |
| [D-FINE](https://github.com/Peterande/D-FINE) | 实时检测 | 无 release；最近提交 2026-10-05 | **Apache-2.0** | RF-DETR 之外的 Apache 备选 |
| [DEIMv2](https://github.com/Intellindust-AI-Lab/DEIMv2) | 实时检测（DINOv3 骨干） | 无 release；最近提交 2026-10-23 | **DEIMv2 License：仅限非商用，明确禁止集成进商业产品、商业部署、SaaS 与商业硬件** | 社区帖子称其为 Apache-2.0，**与原文不符**；原版 DEIM 才是 Apache-2.0 |
| [Ultralytics](https://github.com/ultralytics/ultralytics)（YOLO26 等） / [YOLOE](https://github.com/THU-MIG/yoloe) | 实时检测 / 开放词汇检测 | `ultralytics` 8.4.203 / 2026-11-05 / YOLOE 最近提交 2025-06-26 | **AGPL-3.0**（商用需购买 Ultralytics 企业许可） | 生态最大、边缘部署最方便，但 AGPL 网络服务条款对"策展即服务"（R-19）直接构成传染风险 |

**对本仓库**：
- 清洗与标注（离线）：SAM 2 + Grounded-SAM-2 维持默认；SAM 3 的概念分割对"按衣物类别自动打掩码"很有用，按 SAM License 走 LEGAL 逐项审后再进默认路径。
- 机上实时识别（洗衣房分拣的衣物 / 筐 / 洗标定位，[laundry-sorting-brain-plan.md](laundry-sorting-brain-plan.md)）：检测器用 RF-DETR（确认所用 checkpoint 为 Apache）或 D-FINE；**Ultralytics / YOLOE / DEIMv2 一律不用**，包括"先用着、上线前再换"——训练好的权重与标注格式会被锁进去。
- 这些许可结论要写进 governance U-11 表（§13 第 9–10 项）。

## 13. 对本仓库的启示与回写清单

| # | 事项 | 写回位置 | 优先级 |
|---|---|---|---|
| 1 | 引入 LeRobot 时直接锁 0.7.x；复查 0.6 时代用 `use_peft` 与批量图像增强的实验结论 | [training-pipeline.md](training-pipeline.md)、governance 新增未决项 | 高 |
| 2 | sim 轨资产以 MJCF 为唯一手写源，USD / URDF 由它生成；接触参数随资产版本化 | [sim-track.md](sim-track.md) | 高 |
| 3 | sim 轨任务 API 定为 Isaac Lab 3.0（Newton 后端，免装 Isaac Sim）或 mjlab，二选一前做一次同任务对比 | [sim-track.md](sim-track.md)、governance 新增未决项 | 中 |
| 4 | ROS 2 机器人的录制直接收 rosbag2 MCAP，ingest 只校验不转码 | [ingest-spec.md](ingest-spec.md) | 中 |
| 5 | L1 运动学过滤增加"Pinocchio 逆动力学力矩超限"与"重定向脚滑 / 自穿透"两道门（阈值走消融裁决） | [curation-pipeline.md](curation-pipeline.md) | 中 |
| 6 | 评估 SONIC 作为人形下肢 / 平衡层；权重 license 先核，研究分支先行 | [robot-track-teleop.md](robot-track-teleop.md)、[cleaning-algo-selection.md](cleaning-algo-selection.md) license 列 | 中 |
| 7 | rerun 从 0.36.3 升到 0.42.x，升级前跑 viz 测试 | `pyproject.toml` | 低 |
| 8 | Copper-rs 确定性回放、Genesis、ManiSkill3、TensorRT Edge-LLM 记为观察项，不进默认路径 | 本文 | 低 |
| 9 | U-11 结案 / 改判：第 8 项 MASt3R-SLAM → CC BY-NC-SA，研究分支限定；第 17 项 MoGe-2 代码 MIT（权重待核）；第 21 项 SAM3 补"允许商用、禁用条款"原文要点；第 13、20 项补原文核对 | governance U-11 | 高 |
| 10 | U-11 新增：DEIMv2（非商用）、Ultralytics / YOLOE（AGPL-3.0）、CoTracker（CC BY-NC）、FAST-LIO2 / FAST-LIVO2（GPL-2.0）列为默认路径禁用；cuVSLAM（NVIDIA 平台限定）、VGGT（仅 Commercial 权重）、Depth Anything 3（按权重分）、RF-DETR（按 checkpoint 分）列为有条件可用 | governance U-11 | 高 |
| 11 | 弱纹理兜底默认候选从 MASt3R-SLAM 改为 MapAnything / VGGT-SLAM（商用权重） | [cleaning-algo-selection.md](cleaning-algo-selection.md) §1.7 | 中 |
| 12 | 洗衣房场地：部署前建图并版本化（RTAB-Map / GLIM），作为 Nav2 底图与 sim 场景底图；导航段打子任务标签 | [runtime-and-deployment.md](runtime-and-deployment.md)、[sim-track.md](sim-track.md) | 中 |
| 13 | 机上实时检测器限定 Apache 许可（RF-DETR 指定 checkpoint / D-FINE） | [laundry-sorting-brain-plan.md](laundry-sorting-brain-plan.md) | 中 |
| 14 | 去重特征加 DINOv2 对照（vs SigLIP），走消融裁决 | [cleaning-algo-selection.md](cleaning-algo-selection.md) §1.9 | 低 |

**已同步到**（2026-11-05）：第 1 项 → training-pipeline §3.1 + governance R-15（用 R-15 承接，未新开 U 条目）；第 2 项 → sim-track §2。第 9–10 项 → governance U-11（改 #8 / #13 / #17 / #20 / #21，新增 #33–#43；需 LEGAL 判断的仍标待意见，按 U-29 不批量裁决）。DINOv2 已进 U-11 #44。第 3–8、11–14 项待确认。

## 14. 来源

- GitHub Releases / Tags API（2026-11-05 23:30 EST 复查）：navigation2、rtabmap、glim、kiss-icp、nvblox、cuVSLAM、isaac_ros_visual_slam、map-anything、Hydra、InternNav、rf-detr、ultralytics、Open3D、mediapipe、curobo、TensorRT-Edge-LLM、newton、IsaacLab、IsaacSim、mujoco_warp、lerobot、rerun、dora、copper-rs、Genesis、ManiSkill、mjlab、drake、pinocchio、Grounded-SAM-2、mujoco-usd-converter；crates.io `cu29`
- cuRobo v0.9.0 发布说明：https://github.com/NVlabs/curobo/releases ；Nav2 1.5.3：https://github.com/ros-navigation/navigation2/releases
- PyPI JSON 接口（2026-11-05 实测，同日 23:30 EST 复查）：lerobot、rerun-sdk、mujoco、mujoco-warp、mujoco-mjx、newton、mjlab、isaaclab、mcap、genesis-world、mani-skill、pin、crocoddyl、drake、dora-rs、viser、dex-retargeting、robosuite
- LeRobot v0.7.0 发布说明：https://github.com/huggingface/lerobot/releases/tag/v0.7.0
- Isaac Lab v3.0.0：https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0
- Newton 1.0 GA 公告：https://github.com/newton-physics/newton/discussions/2176 ；LF 新闻稿：https://www.linuxfoundation.org/press/linux-foundation-announces-contribution-of-newton-by-disney-research-google-deepmind-and-nvidia-to-accelerate-open-robot-learning
- MuJoCo Warp 文档：https://mujoco.readthedocs.io/en/stable/mjwarp ；MJX：https://mujoco.readthedocs.io/en/stable/mjx.html
- ROS 2 Lyrical：https://docs.ros.org/en/lyrical/Releases/Release-Lyrical-Luth.html ；RMW 冻结：https://discourse.openrobotics.org/t/upcomming-rmw-feature-freeze-april-6th-2026-ros-lyrical/53696 ；rmw_zenoh：https://github.com/ros2/rmw_zenoh
- rosbag2 默认 MCAP：https://discourse.openrobotics.org/t/psa-default-ros-2-bag-storage-format-is-changing-to-mcap-in-iron/28489 ；https://foxglove.dev/blog/mcap-as-the-ros2-default-bag-format
- Copper-rs：https://copper-project.github.io/copper-rs-book/ch02-copper-vs-ros.html ；https://www.codethink.co.uk/articles/2026/copper-rs-real-time-robotics.html
- Genesis 独立测评：https://stoneztao.substack.com/p/the-new-hyped-genesis-simulator-is ；ManiSkill3：https://arxiv.org/abs/2410.00425
- 资产转换：https://pypi.org/project/mujoco-usd-converter/0.9.0/ ；https://isaac-sim.github.io/IsaacLab/v3.0.0-beta/source/how-to/import_new_asset.html ；https://control.ros.org/kilted/doc/mujoco_ros2_control/mujoco_ros2_control/docs/tools.html ；https://simready.artlabs.ai/compare/urdf-vs-mjcf-for-ros-2
- GR00T-WholeBodyControl：https://github.com/NVlabs/GR00T-WholeBodyControl ；GEAR-SONIC 模型卡：https://huggingface.co/nvidia/GEAR-SONIC
- mjlab：https://github.com/mujocolab/mjlab ；GMR：https://github.com/YanjieZe/GMR
- cuRoboV2：https://arxiv.org/abs/2603.05493 ；https://github.com/NVlabs/curobo
- Jetson Thor GR00T N1.7：https://www.jetson-ai-lab.com/tutorials/groot_n17_on_thor/ ；TensorRT Edge-LLM：https://nvidia.github.io/TensorRT-Edge-LLM/0.11.1/overview.html
- Foxglove：https://www.businesswire.com/news/home/20251112126106/en/Foxglove-Raises-%2440-Million-Series-B-to-Power-the-Future-of-Physical-AI ；https://www.businesswire.com/news/home/20260421818840/en/
- Encord：https://encord.com/blog/data-labeling-platforms-for-physical-ai ；https://www.businesswire.com/news/home/20250612297482/en
- Rerun 查询接口：https://docs.rs/crate/re_datafusion/0.30.0/source/README.md
- §9–§12 各仓库 LICENSE 原文（2026-11-05 经 GitHub API 读取）：cuVSLAM、nvblox、RTAB-Map、GLIM、KISS-ICP、FAST_LIO、FAST-LIVO2、map-anything、vggt（含 README 商用说明）、VGGT-SLAM、MASt3R-SLAM、Hydra、concept-graphs、navigation2、InternNav、NavDP（无 LICENSE）、NaVILA、sam2、sam3、sam-3d-objects、GroundingDINO、Grounded-SAM-2、rf-detr、D-FINE、DEIMv2、ultralytics、yoloe、Depth-Anything-3（README 权重表）、Video-Depth-Anything、MoGe（README）、FoundationStereo、co-tracker、dinov2（README 许可节）、dinov3、DINO-X-API（README）、Open3D、mediapipe
- Isaac ROS 发布说明：https://nvidia-isaac-ros.github.io/v/release-5.0/releases/index.html
- 激光 SLAM 社区基准：https://discourse.openrobotics.org/t/slam-benchmark-on-livox-mid-360-public-dataset-our-own-uav-flight-data-kiss-icp-dlio-fast-lio2-glim/57912
- Nav2 Lyrical 要点：https://discourse.openrobotics.org/t/nav2-lyrical-release-key-features/57666
- VGGT-SLAM 2.0：https://arxiv.org/abs/2601.19887 ；MapAnything：https://github.com/facebookresearch/map-anything
- InternVLA-N1 模型卡：https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN
- RF-DETR 许可页：https://roboflow.com/model-licenses/rf-detr ；YOLO26：https://blog.roboflow.com/yolo26/
