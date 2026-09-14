# 评测协议：真机协议模板 · 指标字典 · 消融判定规则 · 仿真基准

> 2026-09-08。所有"显著优于""达标""收益"在本仓库的唯一定义。承接 architecture §4、training-pipeline §2/§3.2-5、index-replica-plan §6 与诚实性协议（可复现日志 + 干预率记录）。

## 1. 指标字典

### 1.1 数据侧

| 指标 | 定义 | 分母 |
|---|---|---|
| 通过率漏斗 | 各门 `pass / (pass+flag+reject)`，按 track × 门 | 当期入湖 episode 数 |
| 可用训练小时 | `state == training_ready` 的 episode 时长和 | — |
| 每可用训练小时全成本 | （计酬 + 设备摊销 + 平台成本 + HITL 人力）/ 可用训练小时 | 季度 |
| 多样性计数 | 每 1,000 可用训练小时的独特 **任务模板 id / `object_tags` 去重 / `scene_id` / `operator_id`** 数；标签词表版本化，计数按词表版本报 | 策展后（与 Index 的分母口径不同，不直接对比，governance D-09） |
| 伪标签质量 | 金标准配对集上 MPJPE（mm）、EE 位置 RMSE（mm）、姿态 RMSE（°）、夹爪开度 MAE | 配对集版本 |
| 同步残差 | 视觉↔IMU↔动作对齐残差 P95（ms） | 每 episode |
| 欺诈检出率 | 红队植入样本检出数 / 植入数 | 月 |

### 1.2 模型侧

| 指标 | 定义 |
|---|---|
| 成功率 | 任务模板完成判据为真的 trial 比例；95% Wilson 区间一起报 |
| 任务进度分 | 子任务完成数 / 子任务总数，取均值（Wall-OSS 口径） |
| 介入率 | 接管次数 / 自主运行小时；接管时长占比 |
| 吞吐 | 每小时完成任务数（营业级指标，π*0.6 口径） |
| 少样本适应 | 三个刻度并列报告：① 1 条演示零梯度（GEN-1.5 12 s / Skild S1 1 条视频口径）；② 1–5 分钟数据 10 步微调（GEN-1.5 口径）；③ ≤10 h 全量后训练（Dyna-2 口径）。与北极星"新任务上线成本"同口径；换算参考 Skild 自报"1 条演示 ≈ 380 条遥操作"（D-23，只作量级） |
| OOD 分轴 | 背景 / 光照 / 物体 / 场地 四轴各自的成功率下降幅度 |

### 1.3 规模侧

- L(D) 拟合：验证损失 vs 数据小时，`L = (D_c/D)^α`，报 α 与 D_c 及拟合 R²；数据每翻倍重拟合。
- 多样性幂律（Lin 式）：成功率 vs 场景数 / 物体数 / 操作者数，各自单独拟合。

## 2. 仿真基准（评测 CI）

| 基准 | 用途 | 频率 |
|---|---|---|
| LIBERO（四套件） | 每 checkpoint 回归；社区可比 | 每 checkpoint |
| SIMPLEREnv | real-to-sim 一致性 | 每数据版本 |
| Isaac Lab-Arena 自建任务集（与真机任务模板一一对应；场景用 SimFoundry 从真机评测场地视频重建，[research-simfoundry.md](research-simfoundry.md) §5.2） | 消融主战场 | 每数据版本 |
| RoboTwin 子集（双臂） | 双臂任务 | 每数据版本 |
| 长任务规划基准（SimFoundry 孪生 + 任务表亲链成 3–6 步长任务，BDDL 逐步校验；含扰动注入） | S2 规划：子任务进度分、扰动后恢复率、重规划步数 | 每 S2 版本 |

本体 gap：仿真基准用的具身与目标本体不同（LIBERO 是 Franka），所以仿真结论只用于**相对比较**（配方 A vs B），绝对能力以真机为准；Arena 自建任务集用目标本体的 USD，是唯一同具身的仿真基准。

## 3. 真机协议模板

每次真机评测填写并存档（`data/eval/<run_id>/protocol.yaml` + 日志）：

```yaml
run_id: 2026-09-15-stageA-vs-zeroshot
policy: {name, checkpoint_uri, dataset_version, mixture_config_hash}
baseline: {name, checkpoint_uri}
embodiment: robot_model + firmware
tasks: [task_template_id ×N]          # 每任务 ≥20 trial，两组交替（ABAB），操作员盲测
scenes: [scene_id ×≥3]               # 至少一个 held-out 场地
initial_conditions: 种子化物体摆放（照片存档）
success_criteria: 任务模板判据版本
intervention_policy: 何时允许接管、如何记录（robot-track-teleop §4）
logging: MCAP 全量记录（policy_version、deployment_id 必填），rollout 回流入湖
reporting: 成功率 + Wilson 区间、进度分、介入率、吞吐、失败案例视频索引
```

对外任何能力宣称必须能指向一个 run_id 及其日志（诚实性协议）。

## 4. 消融判定规则

- **单位**：一次消融 = 同一代码 commit、同一超参、只变一个因子（数据配方 / 阈值 / 数据量）。
- **显著性**：仿真基准 ≥3 seed，报均值 ± 标准差；真机每任务 ≥20 trial；判定用双侧 Fisher 精确检验（成功率）或 Welch t（进度分），α = 0.05；效应量至少 5 个百分点才算"收益"。
- **Stage A 放行**（training-pipeline §2）："显著优于零样本" = 仿真 Arena 自建任务集上微调后成功率 − 零样本成功率 ≥10 个百分点且 p < 0.05，3 seed。
- **Stage B 止损**：0→1 预训练模型在同一评测上 **不低于** Stage A 微调对照（差 <5 个百分点视为持平，持平不放行）。
- **阈值裁决**（curation §7）：严格化后训练指标不涨（<5 个百分点且不显著）一律回退。
- **功效预估**：20 trial 检测 25 个百分点差异的功效约 0.8；要检测 10 个百分点需 ≥80 trial——报告必须注明本次功效。

## 5. sim-real gap 探针

同任务的 `teleop_replay`（sim-track §3）与真机 episode：轨迹 RMSE、成功率差；gap 超过 20 个百分点的任务簇标记"仿真不可信"，其消融只以真机为准。场景级保真度用 SimFoundry 协议：同一组策略在孪生场景与真机各跑 ≥20 trial，报 Pearson r 与 MMRV（SimFoundry 论文值 0.911 / 0.018，我们自家 3 个任务的门槛 r ≥0.8）；子任务级成功率（对齐 curation 的 segment 边界）通常比整任务相关性更高，两者都报。

## 6. 评测集固定

held-out 规则见 curation §8；评测集版本 `split_version` 与数据集版本一起冻结，所有对比报告必须注明两者。
