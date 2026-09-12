# 人形机器人数据-模型-运行时架构（对标 Figure 03 × Index × Helix 02）

> 综合三轮调研（2026-08-29）：[research-figure.md](research-figure.md)、[research-opensource.md](research-opensource.md)、deep-research 工作流 37 个来源的论断提取（对抗核查阶段未完成，本文以多源交叉印证替代；单一来源的论断已标注）。本文档是本仓库的**总设计**；全部文档的阅读路径见 [README.md](README.md)，风险/未决决策/自报数字登记见 [governance.md](governance.md)。

**术语表**（全仓库统一用法）：

| 术语 | 定义 |
|---|---|
| track（轨） | 采集形态的枚举：robot / human / device / sim；同一 EpisodeMeta，`track` 字段区分 |
| session（会话） | 一名操作员/Creator 一次连续佩戴或开机到关机的采集过程；含多个 episode |
| episode | 一次任务尝试的完整记录（开始→结束/失败/中止），策展与训练的基本单位 |
| segment（子任务段） | episode 内按子任务边界切出的时间区间，带子任务级指令 |
| clip（切片） | 从 segment 再裁出的 3–12 s 干净片段，进演示库（物理提示） |
| 质量门 | 策展五阶段中的自动过滤阶段（门①），含 L1/L2/L3 三级 QC |
| 伪标签工厂 | human 轨从视频恢复动作标签（手部位姿→EE）的处理链 |
| 演示库 | 按任务 embedding 可检索的 clip 集合，训练分片之外的第二产物 |
| 具身转换 | 把穿戴/头戴视角的 device 轨 episode 变换为机器人域 episode 的可选阶段（Skill Transform 式），见 §2.3 |
| 入湖（ingest） | 原始采集文件进入数据湖：校验、时间对齐、转码为 MCAP/AV1 |
| 操作员（operator） | robot/device 轨的采集者；human 轨对应词为 Creator |
| 再平衡 | 策展门④：按任务/场景配额与 embedding 聚类调整采样权重 |

---

## 1. Figure 数据飞轮全景：四条数据来源

Figure CEO 公开口径（Forbes 2026-08-26）：数据战略 = **仿真/合成数据 + 人类演示 + 机器人自身行动数据**三源并举（互联网数据为 VLM 骨架的第四源）。对应到基础设施：

```
互联网数据 ──────────► S2 VLM 骨架预训练（开源 7B VLM，非 Figure 自采）
Index 人类第一视角视频 ─► 预训练中层（规模腿：30 min/s 入库，$1B/12mo）
仿真 + 动捕重定向 ──────► S0 全身控制（20 万并行环境 + 1,000h 重定向动捕）
Figure 03 车队真机数据 ─► S1/S2 微调（精度腿：500h 级精策划遥操作 + 车队回流）
```

### Figure 03 × Index 的关联：一对协同设计的采集终端

两者是同一数据引擎的两端，多处硬件/管线决策互为镜像：

| 维度 | Figure 03（机器人轨） | Index（人类轨） |
|---|---|---|
| 角色 | 精度腿：全模态+动作真值 | 规模腿：纯视频、无动作标签 |
| 采集端 | 头部相机（帧率×2、延迟×¼、FOV+60%）+ 双掌心相机 + 指尖 3g 触觉（自研）+ 全身本体感知（相机总数未公开 ⚠️；见 [research-figure.md](research-figure.md) §5） | 手机 App 优先 + 头戴第一视角录制设备补充 |
| 传输 | 10 Gbps mmWave 回坞卸数（TB 级/班次，店转发） | 消费级公网上传 |
| 供能闭环 | 2 kW 足底无线充电（回坞=充电+卸数，官方数字，research-figure §5） | 按分钟计酬（$15M 已付） |
| 规模引擎 | BotQ 量产（12,000 台/年 → 10 万台） | 众包（108 国、4.4 万周活、双边市场） |
| 策展 | 精策划（8h 数据即可出策略，data quality manager 岗位） | 五阶段自动化策展管线 |

**协同设计的证据链**：(a) Figure 03 相机架构官方明说"purpose-built for Helix 高频视觉运动控制"；(b) Go-Big 已验证纯人类视频→机器人导航的零样本迁移（SE(2) 速度指令端到端），Index 的数据才有明确消费者；(c) 采集环境=部署环境（Brookfield 物业既供 Index 采数又供机器人部署），刻意最小化域差；(d) 学术印证：PrimeU 论文（2026-06）证明人类视频零样本迁移**依赖人形本体与人类形态对齐的协同设计**——Figure 03 的类人形态本身就是 Index 数据能用的前提。

---

## 2. 数据管线（采集 → 上传 → 清洗/分拣/QC → 标注 → 训练集）

### 2.1 Index 五阶段策展管线（官方披露，两独立来源印证）

1. **自动过滤**：技术/视觉/语义三层质量筛（分辨率、帧率、光照、内容有效性）
2. **人工欺诈审查**：用户账户级审计（按分钟计酬必然催生刷量，欺诈检测是一等公民）
3. **向量去重**：embedding 相似度阈值去重
4. **再平衡**：任务配额 + embedding 聚类，主动偏置罕见边缘案例
5. **分层标注**：每个 episode 层级化文本 caption（任务级 + 操作级）

多样性即 KPI：每 1,000 小时 = 373 任务 / 1,146 物体 / 116 环境。注意（Forbes）：五阶段会**丢弃大部分原始上传**——可用训练数据远小于 1,600 万条的名义规模。

### 2.2 机器人轨管线（Helix 官方 + 学术拼图）

- 采集：Pilot 遥操作 + 车队自主运行数据；回坞批量卸数（store-and-forward）
- 语言标注：auto-labeling VLM 对分段机载视频事后反推指令（"你会给机器人什么指令？"）
- 开源可复刻的 QC 模板（Ego2Robot，2026-08）：**L1 运动学/几何过滤**（IK 失败、自碰撞、动作离群、工作空间覆盖）→ **L2 统计轨迹过滤** → **L3 VLM 语义审计**
- 人类视频→动作标签（当没有遥操作真值时）：21 手部关键点 → 末端执行器表征，Savitzky-Golay 平滑位置/夹爪宽度 + 高斯加权 SLERP 平滑姿态（Ego2Robot 配方，[arXiv:2608.02580](https://arxiv.org/abs/2608.02580)，≈12.8× 数据放大：1,933h 人类视频 → 15 种本体 24,808h 演示，数字取 [research-qwen-robotics.md](research-qwen-robotics.md) 的更新口径）

各层实施规范：清洗/分割/标注见 [curation-pipeline.md](curation-pipeline.md)，算法选型与 license 见 [cleaning-algo-selection.md](cleaning-algo-selection.md)，device 轨见 [device-track-umi.md](device-track-umi.md)，众包平台见 [index-replica-plan.md](index-replica-plan.md)。

### 2.3 具身转换阶段（可选，device 轨穿戴/头戴子形态）

UMI 式手持夹爪靠腕装鱼眼保证"本体不入观测"，无需转换；但穿戴孪生手套（Sunday 式）与穿戴外骨骼（TwinDEX 式）走**头戴观测**，人体手臂/身材会入画且各采集员运动学不一。对这类子形态，在 ingest 与 curation 之间插入可选的**具身转换阶段**（Skill Transform 式）：输入 device 轨原始 episode，输出机器人域 episode（人体抹除 + 机器人臂合成 + 跨采集员运动学归一化，配方对标 Ego2Robot 六步与 Sunday 自报 90%+ 成功率）。规则：转换结果作为**派生产物**入 lineage（`parent_episode_id` 指向原始），raw 永存；转换失败是质量标记（`reject_embodiment_transform`）不是删除；转换模型版本与权重哈希进 lineage（与 [cleaning-algo-selection.md](cleaning-algo-selection.md) 三条全局纪律一致）。该阶段的触发条件由 EpisodeMeta 的 `device_id` 对应的设备档案决定，human 轨不经过此阶段（human 轨走伪标签工厂）。依据：[research-sunday.md](research-sunday.md) §4.2、[research-twindex.md](research-twindex.md)。

---

## 3. 模型训练（对标 Helix 02 三层）

### 3.1 S2 骨架（大脑）预训练

- Helix S2 = 开源开放权重 7B VLM（互联网规模预训练）+ 500h 机器人演示微调；**不是 Figure 从零训练**
- S2→S1 接口：S2 输出**单个连续潜向量**，投影进 S1 token 空间与 S1 自身视觉特征拼接；S2 异步后台运行（7–9 Hz）
- Helix 端到端**单阶段训练、单套权重**、标准回归损失，无任务专属头
- 本仓库 S2 规划语料的来源分工：human/robot 轨的事后反推分层标注提供**语言多样性**；sim 轨 `planning_trace`（SimFoundry 孪生 + BDDL 谓词目标 + 仿真校验的子任务完成/失败/重规划轨迹，[sim-track.md](sim-track.md) §3）提供**可验证的接地语料**与长任务评测。后者对 S2 的收益是我们的推断（governance U-21），不单独撑 S2
- 人类视频进预训练的开源验证：GR00T N1 数据金字塔（真机+人类视频+合成，端到端联训）；Ego2Robot 1:1 混合共预训练把干净任务成功率 62.2%→68.1% 且 OOD 泛化一致提升
- 规模换参数的证据：Octo 93M 训 80 万演示 ≈ RT-2 55B；OpenVLA 7B 训 97 万 OXE episode > RT-2-X 55B——**中等模型 + 大而多样的数据集是可行开源路线**

### 3.2 S1 / VLA 动作专家

| 方案 | 骨架 | 动作头 | 频率 | 备注 |
|---|---|---|---|---|
| Helix S1 | 80M cross-attn enc-dec，**视觉主干完全在仿真中预训练** | 回归 | 200 Hz | 潜向量条件化 |
| π0 | 3B PaliGemma | ~300M flow matching，chunk H=50 | 50 Hz | 论点：离散自回归动作 token 太慢 |
| GR00T N1 | 2B Eagle-2 VLM | diffusion transformer | 120 Hz | 与 S2 联训不冻结 |
| LeRobot 可复现 | — | ACT（52M，100–200 Hz）/ Diffusion Policy / SmolVLA 450M / π0 | — | π0 支持 `train_expert_only=true` 冻结 VLM 只训动作专家 |

### 3.3 S0 全身控制

完全仿真训练：20 万+ 并行环境 + 大规模域随机化 + 1,000h+ 关节级重定向人体动捕；10M 参数，1 kHz，关节状态+基座运动 → 执行器指令。开源对标：Isaac Lab RL + mocap retargeting。

---

## 4. 验证与评测

- 数据缩放消融内建化：Figure 以 10/20/40/60h 切分跑缩放曲线决定采集预算（60h vs 10h 吞吐 +58%）
- 仿真回归：Isaac Lab-Arena 批量策略评测；真机前先仿真
- 质疑视角（必须内建）：BMW 曾公开反驳 Figure 的部署宣称（单台/非生产时段 vs "每天端到端运营"）；81 小时分拣直播被质疑遥操作痕迹。→ 我们的评测协议要求**可复现日志 + 干预率记录**，杜绝"零干预"式不可验证宣称

## 5. RL 闭环（离线 + 在线）

Helix 的 runtime 线索：内建 **OOD 检测 + 自动 reset/recovery** 机制（策略失去信心即重置续跑）——车队数据回流 + OOD 事件即在线闭环的数据源。开源可落地方案（多来源验证）：

1. **HIL-SERL**（LeRobot 内置）：离线示教训练奖励分类器（ResNet10, 128×128 ROI）→ 分布式 SAC actor-learner（gRPC，默认 4s 推权重）→ 人类可随时介入纠正。**真机 1–2 小时达到近满成功率**；人类介入把收敛步数削减到 ~¼；EE 空间 + 工作空间边界（关节空间几乎学不会）；SERL 前向/后向控制器自动 reset。
2. **残差 RL（HiL-ResRL，2026-06）**：冻结基础 VLA（π0.5/Diffusion Policy 均可），只训轻量残差策略 a = a_base + a_res（离策略 SAC）；真机 ~1.5h 到 95%+；力觉感知变体在接触密集任务 50%→93%（印证 Figure 03 指尖触觉对 RL 的价值）；HIL 变体紧急停止 2 次 vs 全自主 15 次。
3. **离线→在线混合**：纯在线 RL 样本效率不足，replay buffer 注入离线数据是标准做法。

## 6. 核心问题点（开放风险）

1. **具身鸿沟**：人类视频无动作标签。潜动作模型（LAPA 式）在操作任务上表现差（MetaWorld 0.14 vs 光流中间表征 SOF 0.69）；光流/重定向等**显式中间表征**目前更可靠。零样本迁移依赖本体与人类形态对齐（PrimeU）。
2. **触觉/力学缺失**：人类视频不含触觉与力反馈，Index 数据能撑多深的接触密集操作未被证明。
3. **众包质量与欺诈**：可用数据远小于名义规模；欺诈审查必须是管线一等公民。
4. **宣称可信度**：Figure 关键数字（车队规模、零干预）有第三方反驳先例，架构设计不能按其宣传口径过度乐观。
5. **经济账**：人类视频吞吐是遥操作的 4.8–7.2×（PrimeU 实测），但仍需真机数据封顶——human 轨与 robot 轨缺一不可。

风险的正式登记（含 owner 与复检时点）在 [governance.md](governance.md)；本节只保留设计层面的问题陈述。

### 6.5 采集哲学：接口对齐 vs 表征对齐

四轨采集背后是两种弥合"人→机器人具身鸿沟"的对立哲学，本仓库刻意并行两者：

| | 接口对齐（UMI/Data Hands，device 轨） | 表征对齐（Index/头戴视频，human 轨） |
|---|---|---|
| 思路 | 采集端物理消灭 gap：人与机器人共用同一观测-动作接口（腕装鱼眼 + 同款夹爪 + EE 相对位姿动作） | 数据端全覆盖，靠算法弥合 gap（手部重定向、光流等中间表征） |
| 泛化保证 | 由构造保证：训练/部署分布同构，本体不入观测、动作与关节解耦 | 由模型保证：依赖重定向质量与共训练配方 |
| 代价 | 泛化锚定在"同款末端执行器"，换灵巧手需适配（GEN-1 实测 2.5–11.4% 参数变化） | 伪标签精度上限、触觉缺失 |
| 任务覆盖 | 平行夹爪任务子集 | 全部日常任务 |
| 规模证据 | Generalist 50 万+ 小时 → GEN-1.5 物理提示涌现 | Index 1,600 万条 + Go-Big 导航零样本迁移 |

共同点：**接口对齐消灭鸿沟、规模多样性提供燃料，二者缺一不可**。device 轨与 human 轨的配比不由立场决定，由下游消融（含少样本适应基准）裁决——这是"多采集方式并行"决策（schema 四轨）的理论依据。device 轨实施见 [device-track-umi.md](device-track-umi.md)。

## 7. 本仓库的开源架构方案

```
┌─────────────── 采集层（多方式组合，配比由消融裁决）─┐
│ robot 轨:  遥操作(Quest3/OpenTeach 路线)             │ MCAP 记录(多流单文件,append-only)
│ human 轨:  头戴/手机第一视角视频(无动作标签)          │ 环形缓冲 + 断点续传 + 坞站批量同步
│   └ 后续: Creator App 手机众包(场景扫描→个性化任务→谓词验收) │
│ device 轨: UMI/Data Hands 式手持夹爪(硬件动作真值)    │
│ sim 轨:   Isaac Lab/DexMimicGen rollout             │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────── 入湖层 ───────────────┐
│ ingest: 校验/时间对齐/转码(AV1 yuv420p 硬编优先) │
│ [可选] 具身转换(穿戴/头戴 device 子形态, §2.3)     │
│ 五阶段策展: 质量门 → 欺诈/来源审计 → embedding 去重 │
│            → 多样性再平衡 → VLM 分层标注(任务+子任务) │
│ QC 三级: L1 运动学过滤 / L2 统计过滤 / L3 VLM 语义审计 │
└──────────────────┬───────────────────┘
                   ▼
┌─────────────── 数据集层 ─────────────┐
│ LeRobotDataset v3 (parquet+mp4, 流式)  │
│ 分层采样率 schema: 视觉 10–30Hz(S2) / 状态动作 100–200Hz(S1) │
│   (device 轨动作流按传感器原生频率 ≥50Hz 入湖, 不上采)   │
│ 版本化+可空模态(mask) / 人类轨无动作标签→重定向伪标签 │
│ 内建缩放消融切分器(按小时/任务/操作员)  │
└──────────────────┬───────────────────┘
                   ▼
┌─────────────── 训练层（详细设计见 training-pipeline.md）─┐
│ fdp-policy 参考栈: 开源 VLM 骨干(0.5B→4B→7B 阶梯) +      │
│   flow-matching DiT 头; 统一槽位向量+掩码; 相机系增量动作;  │
│   具身感知提示; 演示入上下文接口(物理提示)                  │
│ 课程: A 微调验证 → B 两段式 0→1 预训练(token→flow) →      │
│   C 任务 SFT → D RL 闭环(QC 标记→奖励分类器→HIL-SERL/残差) │
│ 工具: mixture-runner / scaling-fitter / fewshot-bench /    │
│   reward-trainer / eval-CI; 数据配方 yaml 版本化入 lineage  │
│ S0: (范围外, 对接 Isaac Lab)                              │
└──────────────────┬───────────────────────────────────────┘
                   ▼
┌─────────────── 运行时层 ─────────────┐
│ 异步推理: PolicyServer/RobotClient(LeRobot 实测吞吐×2) │
│ OOD 检测 + 自动 reset; 干预率/事件日志回流入湖 → 闭环  │
└──────────────────────────────────────┘
```

### 落地阶段（工程里程碑 M1/M2/M3，按管线层）

- **M1 采集与格式**（本仓库当前目标）：MCAP 采集器 + 时间对齐 + LeRobotDataset v3 导出 + rerun 可视化 QC
- **M2 策展管线**：五阶段策展（质量门/去重/再平衡/VLM 标注）+ L1-L3 QC + 缩放消融工具
- **M3 训练与闭环**：动作专家微调配方 + HIL-SERL 接入 + 异步推理运行时

Index 复刻的硬件/平台时间线用另一套前缀 **H0/H1/H2**（[index-replica-plan.md](index-replica-plan.md) §7），两套对应关系：H0 依赖 M1 完成（能入湖、能导出）；H1 依赖 M2（全自动策展）；H2 依赖 M3（训练闭环 A/B）。设备硬件阶段 P0/P1/P2 是第三套前缀，只描述采集硬件成熟度。

### 能力 → 模块 → CLI → 里程碑

| 能力 | `src/fdp/` 模块 | CLI 子命令 | 里程碑 | 规范文档 |
|---|---|---|---|---|
| 多流采集写 MCAP、断电耐崩、时间戳 | `recorder` | `fdp record` | M1 | [recorder-sync-and-storage.md](recorder-sync-and-storage.md)、§8 |
| 入湖校验/对齐/转码/幂等 | `ingest` | `fdp ingest` | M1 | [ingest-spec.md](ingest-spec.md)、[data-format-contract.md](data-format-contract.md) |
| 四轨 EpisodeMeta、版本迁移 | `schema` | — | M1 | [data-format-contract.md](data-format-contract.md) |
| LeRobotDataset v3 导出、双视图、归一化统计 | `export` | `fdp export` | M1 | [data-format-contract.md](data-format-contract.md) |
| rerun 检视 | `viz` | `fdp viz` | M1 | — |
| 五阶段策展、QC 三级、分割/标注/演示库 | `curation` | `fdp curate` | M2 | [curation-pipeline.md](curation-pipeline.md)、[cleaning-algo-selection.md](cleaning-algo-selection.md) |
| 具身转换（可选阶段） | `curation.embodiment` | `fdp curate --stage embodiment` | M2 | §2.3 |
| 缩放消融切分器 | `curation.splits` | `fdp curate --split` | M2 | [eval-protocol.md](eval-protocol.md) |
| 训练配方/消融/评测 CI | 独立仓库 fdp-policy | — | M3 | [training-pipeline.md](training-pipeline.md) |
| 运行时回流 | `ingest`（robot 轨来源之一） | `fdp ingest --source fleet` | M3 | [runtime-and-deployment.md](runtime-and-deployment.md) |

## 8. 时间基准与同步

多流对齐是数据可用性的命门（[index-replica-plan.md](index-replica-plan.md) §1 时钟行）。本节定义全仓库的时间语义，ingest 校验（[ingest-spec.md](ingest-spec.md)）与 curation 拒收判据（[curation-pipeline.md](curation-pipeline.md) §1.1）都以此为准。

### 8.1 时间戳语义

- 每条消息带两枚时间戳（MCAP 原生字段）：`log_time`（写入记录器的时刻）与 `publish_time`（传感器/驱动声明的采样时刻）。**训练与对齐只用 `publish_time`**；`log_time` 只用于诊断记录延迟。
- 单位一律 ns，int64；episode 内使用**单调时钟**（`CLOCK_MONOTONIC_RAW` 或设备等价物），episode 元数据另存一枚"单调→UTC"的偏移量（`started_at_ns` 为 UTC 纳秒），跨设备/跨会话比较只在 UTC 层做。
- 视频流：每帧一枚 `publish_time`，取**曝光中点**（非帧到达时刻）；全局快门相机直接用，卷帘快门相机记录曝光起止并在标定文件里声明行读出时间。
- 动作/状态流：`publish_time` 为采样时刻；遥操作动作另记 `command_time`（发出时刻）以量化闭环延迟。

### 8.2 多流同步手段与可达精度

| 手段 | 适用 | 可达精度 | 成本/备注 |
|---|---|---|---|
| 硬件触发（相机 GPIO 同步脉冲 + IMU 同步） | robot 轨多相机、自研头戴设备 P1 | <0.1 ms | 需全局快门与触发线；P1 设备的默认方案 |
| 同一 SoC 单时钟域软同步 | 手机、GoPro 单机 | 1–5 ms | 无额外硬件；视频与 IMU 同源即可 |
| PTP（IEEE 1588）/ 有线 NTP | 机器人本体多计算板 | PTP <0.1 ms、NTP 1–10 ms | robot 轨跨板必须 PTP |
| 事后相关对齐（IMU 角速度 vs 视觉旋转、音频拍手/LED 闪烁标记） | device 轨 GoPro + 外部 IMU、多设备同穿戴校准 | 1–3 ms | 零硬件；ingest 内建，产出对齐残差进 QC |

### 8.3 跨时钟域对时

- 每个物理设备 = 一个时钟域，episode 元数据里记录所有参与时钟域及其对 UTC 的偏移与漂移估计（`clock_domains[]`，字段契约见 [data-format-contract.md](data-format-contract.md)）。
- 多设备同录（如头戴 + UMI 同穿戴校准）：会话开始与结束各做一次**同步事件**（LED 闪烁 + 拍手，双设备可见/可闻），ingest 用它估计偏移与线性漂移；漂移 >1 ms/min 的会话标记 `flag:clock_drift`。
- 机器人本体：本体主控为时间主，相机/触觉/遥操作端全部对齐到主控 PTP 时钟；遥操作端（Quest 3 等）走 NTP 到主控并在 ingest 用动作-状态互相关再校一次。

### 8.4 同步误差预算

以动作专家 100–200 Hz 消费为约束（一个控制周期 5–10 ms）：

| 流对 | 预算 | 依据 |
|---|---|---|
| 视觉 ↔ 动作/状态 | ≤5 ms（robot/device 轨）；≤15 ms（human 轨，仅供伪标签） | 一个 200 Hz 控制周期内；human 轨无动作真值，要求放宽 |
| IMU ↔ 视觉 | ≤2 ms | VIO 收敛条件（Kalibr/ORB-SLAM3 经验值） |
| 多相机彼此 | ≤1 ms（硬件触发）/ ≤10 ms（软同步，仅允许 human 轨） | 立体/多视角一致性 |
| 触觉 ↔ 动作 | ≤2 ms | 接触事件对齐 |

超预算的 episode 不删除，标记 `flag:sync_budget_exceeded` 并从 robot/device 轨训练分片排除，可留在 human 轨消费路径。

### 8.5 标定工序与漂移再估计

- **出厂标定**：相机内参 + 相机-IMU 外参 + 时间偏移（Kalibr 标准工序，棋盘/AprilGrid），产出标定文件随设备档案走（`device_id` → `calibration_ref`），每条 episode 引用标定版本。
- **在线再估计**：每次 ingest 用 VIO 残差与 IMU-视觉时间偏移估计值与出厂值比对；偏差超阈值（时间偏移 >1 ms、外参旋转 >0.5°）的设备进入"待重标"队列，其数据标记 `flag:calib_stale`。
- **规模化纪律**：几十台以上设备时标定一致性成为主要误差源（[device-track-umi.md](device-track-umi.md) §4），标定文件哈希进 lineage，任何重标产生新的标定版本而非覆盖。

主要来源：Figure 官方（[Helix](https://www.figure.ai/news/helix)、[Helix 02](https://www.figure.ai/news/helix-02)、[Figure 03](https://www.figure.ai/news/introducing-figure-03)、[Go-Big](https://www.figure.ai/news/project-go-big)、Index 2026-08-25 发布）；论文：GR00T N1 (arXiv:2503.14734)、π0 (Black et al. 2024)、HIL-SERL (arXiv:2410.21845, LeRobot 实现)、Ego2Robot (arXiv:2608.02580)、PrimeU ego-exo (2026-06)、HiL-ResRL (2026-06)、SOF (2025-12)、Open X-Embodiment (arXiv:2310.08864)、DROID (arXiv:2403.12945)；质疑来源：Fortune/BMW 报道 (2025-11)、81 小时直播争议 (2026-05)。
