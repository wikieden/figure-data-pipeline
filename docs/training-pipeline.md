# 模型与训练层设计（M3 实施蓝本）

> 2026-09-04。综合全部调研（[research-vla-pretraining.md](research-vla-pretraining.md)、[research-qwen-robotics.md](research-qwen-robotics.md)、[research-generalist-dora.md](research-generalist-dora.md)、[architecture.md](architecture.md)）收敛成本仓库自己的模型/训练/工具链设计。原则：**数据引擎优先，模型设计保守**——每个模型决策抄已被 ≥2 家独立验证的共识，创新预算全部留给数据层。

---

## 1. 模型设计：fdp-policy 参考栈

### 1.1 定位与规模阶梯

数据引擎优先的中等模型路线（Octo 93M≈RT-2 55B、OpenVLA 7B>RT-2-X 55B 的规模换参数证据；GEN-0 骨化相变给出下限）：

| 档位 | 骨干 | 触发条件（与 research-vla-pretraining §5 一致） | 用途 |
|---|---|---|---|
| S（0.45–0.5B） | SmolVLA 类 / Qwen-VL 最小杯 | 现在；混合等效数据 **<1e3 小时**时的唯一 0→1 档位（GEN-0 骨化：小数据喂大模型是浪费） | 管线正确性验证、消融快跑、CI 回归、首次 0→1 预训练（数据阶段 B） |
| M（2–4B） | Qwen-VL 3B/4B 级（Apache） | 混合等效 **5e3–1e4 小时**、具身数 ≥10 | 跨具身预训练主力（GR00T 2.2B / π0 3.3B / Wall-OSS 4B / 通义 Manip 同带；数据阶段 C） |
| L（7B+） | 届时最强开源 VLM | **>1e4 小时 / 20+ 具身**且 M 档已在缩放曲线上未饱和 | 跨具身零样本（RDT2 档位） |

档位切换只看两个量：混合等效小时数（按 [research-vla-pretraining.md](research-vla-pretraining.md) §5 的门槛）与 scaling-fitter（§3.2）给出的 L(D) 曲线是否仍在下降；不按日历切换。

**不自研骨干**。VLM 主干永远取自开放权重生态，我们的护城河在数据与后训练。

### 1.2 架构决策（每条注明共识来源）

1. **VLM 主干 + flow-matching DiT 动作头**（π0/GR00T/RDT2/通义四家共识）；AdaLN 条件注入：去噪步、末端执行器类型、相机参数有无（通义配方）。
2. **动作表征两阶段课程**：预训练期离散动作 token（FAST 类）做"梯度桥"，部署期流匹配头（π0.5/Wall-OSS/RDT2 三家独立收敛）。
3. **统一状态-动作表征**：定长槽位向量 + **二值有效掩码**（RDT 128 维与通义 80 维同思路）；槽位布局 = 关节位 + EE 位姿(3D pos+6D rot) + 夹爪 + 灵巧手 + 底座速度，四轨数据（robot/device/human 伪标签/sim）全部映射进同一布局。export 层同时输出 π0 兼容视图（M1 导出即可用 openpi 微调，Stage A 的前提）。
4. **相机系增量 EE 动作**为主动作空间（UMI/通义共识：视觉相似的动作数值相近=跨具身泛化的表征基础）；相机外参 CaPE 式注入、内参进视觉 token（通义）；同时保留关节空间槽位（S0/全身场景后备）。
5. **具身感知提示条件**：通义模板逐字起步（`The robot is {robot_tag} with ... The control frequency is {FPS} Hz. Predict the next {chunk_size} actions: {instruction}`），机器人平台/频率/chunk 长度全走 prompt——新具身零架构改动。
6. **物理提示（演示入上下文）从 day one 设计进接口**：观测序列允许拼接 3–12s 演示片段 token（GEN-1.5 证明该能力随规模涌现，但**接口必须预留**——上下文里留 demo 槽位不花钱，事后加要动架构）。
7. **分层频率消费**：模型输入视觉 ~10Hz + 状态 100–200Hz + 动作 chunk 输出（H=50 起步，π0 口径），与 schema 分层采样率一一对应；**不采用** GEN-0 连续时间异步流（单家未复现，风险预算不批）。
8. **不做 S0**：全身 1kHz 控制层留给 Isaac Lab 生态，我们的模型栈止于 S1 等价层。

### 1.3 明确不抄的东西（负设计）

- Harmonic Reasoning 统一异步流：仅 Generalist 一家、细节未公开 → 观察名单
- 自回归离散动作做部署头：π0 论点 + 实时性证据充分 → 弃
- 每具身独立 MLP 头（GR00T 式）：与我们"新增采集形态=新增 track 值不改 schema"哲学冲突，掩码槽位更干净

---

## 2. 训练课程（四阶段 + 持续评测）

命名约定：本节 **Stage A–D 是训练课程阶段**（做什么训练）；[research-vla-pretraining.md](research-vla-pretraining.md) §5 的**阶段 A/B/C 是数据规模阶段**（有多少数据时允许做什么）。对应关系：Stage A ⇔ 数据阶段 A（微调验证）；Stage B 在数据阶段 B 用 S 档、进入数据阶段 C 后换 M 档；Stage C/D 不受数据阶段限制，任何档位都跑。

```
Stage A 管线验证    微调 openpi(π0)/SmolVLA on 10–50h 精策划 robot 轨数据（LoRA，单卡）
                    通过判据：仿真基准显著优于零样本；证明数据层无毒
Stage B 0→1 预训练  数据 <1e3h 不启动；1e3h 起 S 档，5e3–1e4h 起 M 档（§1.1）；
                    先离散 token 后流匹配两段课程；
                    数据配方 = 四轨混合（human 打底 / sim 中层 / device+robot 顶层，
                    目标域 ≤5%，广度优先）
                    止损门：不超 Stage A 微调对照 → 回退查数据
Stage C 后训练      任务 SFT（高质量分层过滤子集）+ 演示库物理提示评测
Stage D RL 闭环     奖励分类器（QC 成功/失败/介入标记直接当标注）→
                    HIL-SERL / 冻结基座+残差 SAC；SimpleVLA-RL 式单轨迹冷启动
持续    评测 CI     每个 checkpoint 自动跑 LIBERO/RoboTwin 子集 + 少样本适应基准
                    （协议与指标字典见 eval-protocol.md）
```

**数据配方是一等公民版本化产物**：`configs/mixtures/*.yaml` 声明各轨/各任务簇/各质量层的采样权重与温度，配方文件哈希进训练 run 元数据——任何模型可回溯到确切数据配方（lineage 延伸到训练层）。

## 3. 训练工具链

### 3.1 直接采用（不重造）

| 工具 | 用途 |
|---|---|
| lerobot 训练栈 + StreamingLeRobotDataset | dataloader/策略实现基座 |
| openpi | π0 微调参考（Stage A）、`train_expert_only` 配方 |
| Isaac Lab-Arena / LIBERO / RoboTwin | 仿真评测 |
| lerobot HIL-SERL 实现 | Stage D actor-learner 基座 |

### 3.2 自建（差异化所在，M3 交付物）

1. **mixture-runner**：读配方 yaml → 构建混合流式数据集 → 提交训练 → 登记 lineage。消融=多配方并行。
2. **scaling-fitter**：对消融结果拟合 L(D)=(D_c/D)^α（GEN-0 式）+ 按场景/物体/操作者切分的多样性幂律检验（Lin 式），输出"下一小时数据该采什么"的预算建议——**这是数据引擎的方向盘**。
3. **fewshot-bench**：演示库抽 1 条/5 分钟数据 → 零梯度 in-context 与 10 步微调两种评测（GEN-1.5 口径）——比全量微调更灵敏的数据质量探针。
4. **reward-trainer**：从 QC 状态机的 success/failure/intervention 标记批量训练任务奖励分类器（ResNet 小模型），Stage D 与 L3 语义审计共用。
5. **eval-CI**：checkpoint 触发的仿真回归 + 指标仪表盘；真机协议模板（盲测 A/B、干预率记录——诚实性协议的执行工具）。

## 4. 对既有管线层的升级（本设计反推的改动）

| 层 | 升级 | 依据 | 状态（2026-09-08） |
|---|---|---|---|
| schema | EpisodeMeta 增加 `success: bool \| None` 与 `intervention_ts_ns: list[int]`（robot/device 轨）；SignalStream 增加 `slot: str \| None`（声明映射到统一槽位向量的哪一段） | §2 Stage D、§1.2-3 | 已落地 `src/fdp/schema.py`（字段契约见 [data-format-contract.md](data-format-contract.md)） |
| export | 双视图输出：统一槽位+掩码视图（自家训练）与 π0 兼容视图（Stage A）；归一化统计按轨×具身分开存 | §1.2-3 | 待实现（M1） |
| curation | 演示库切片增加"物理提示可用"质量位（干净起止、单原子动作）；QC 标记进 reward-trainer 数据源 | §3.2-3/4 | 待实现（M2） |
| viz | rerun 增加"槽位向量+掩码"面板（调试跨具身映射错位） | §1.2-3 | 待实现（M1 基础面板 / M3 槽位面板） |
| configs | 新增 `configs/mixtures/`；所有阈值/配方 yaml 化并哈希入 lineage | §2 | 目录已建（仅 README），配方待写 |

## 5. 风险与观察名单

1. **两段动作课程的切换成本**（token→flow 迁移期性能坑）：Wall-OSS/RDT2 论文附录为准，Stage B 前做小规模预演。
2. **物理提示是否在 M 档（2–4B）涌现**：GEN-1.5 未公布参数量，可能需要 L 档才出现——fewshot-bench 从 Stage B 起持续测，不等 L 档。
3. **相机系增量动作对移动底座任务的适配**（相机自身在动）：通义已含移动底座配置，抄其处理；不行则退回世界系。
4. 观察名单：Harmonic Reasoning 细节披露、V-JEPA 2-AC 后续（世界模型当策略）、GR00T N2 若改统一动作空间则重新评估。
