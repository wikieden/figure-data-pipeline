# 项目计划：里程碑验收矩阵 · 人力 · 预算

> 2026-09-08。三套前缀（M 工程 / H 硬件平台 / P 硬件成熟度）的统一验收矩阵，以及人力与预算总盘。金额为量级估算，用于排序和止损，不是采购报价；每季度按实际重算（governance R-02）。

## 1. 统一时间线

```
月     0        3        6        9        12       18
工程   M1 ───────►M2 ─────────────►M3 ──────────────►
硬件   H0 ───────►H1 ─────────────►H2 ──────────────►
设备   P0 ───────►P1 ────────────────────────►P2 ───►
训练   Stage A(M1 内)   Stage B(S 档, ≥1e3h)   Stage B(M 档, ≥5e3h)/C/D
```

依赖：H0 等 M1（能入湖、能导出）；H1 等 M2（全自动策展）；H2 等 M3（训练闭环）；P1 硬件投入等 H0 的"伪标签→仿真收益"止损门通过。

## 2. 验收矩阵

| 里程碑 | 交付 | 验收判据（可测） | 阻塞项 |
|---|---|---|---|
| **M1** 采集与格式 | recorder（MCAP）、ingest、export（LeRobot v3 双视图）、viz、schema 0.2、CI | 断电恢复 20/20；同步残差在预算内；0.1 fixture 可迁移；一条真实 episode 走完 record→export 并被 openpi/lerobot 不改代码读入；docs 链接扫描零错 | U-01 中间件、U-03 lerobot-dataset API |
| **M2** 策展 | 五阶段 + QC 三级 + 分割/标注/演示库 + held-out + 消融切分器 + 过渡阈值 | 漏斗仪表盘上线；伪标签金标准 MPJPE 报告；license 终审完成（U-11）；held-out 泄漏检查零命中 | U-11、U-16 过渡方案 |
| **M3** 训练与闭环 | mixture-runner、scaling-fitter、fewshot-bench、reward-trainer、eval-CI、运行时回流 | Stage B 止损门可判；每 checkpoint 自动跑 LIBERO；一次 RECAP 式后训练 run 闭环 | Stage B 数据门槛 |
| **H0** 0–3 月 | 手机 P0 + UMI ×2 + 1 台本体 + 平台 MVP + 伪标签 v0 | 100 可用训练小时；伪标签训出仿真可见收益（eval-protocol §4）；Stage A 放行 | M1 |
| **H1** 3–6 月 | 自研头戴 EVT 10–50 台 + 全自动策展 + 任务配额闭环 + 3–5 台本体 | 每可用训练小时全成本 < 遥操作 1/3（中间点）→ 1/5；多样性 KPI 季度环比提升；末端消融（U-04）完成 | M2、U-04 |
| **H2** 6–12 月 | DVT→PVT 500+ 台 + 千人 Creator + 训练闭环 A/B | 真机 A/B 证明 human 轨显著收益；欺诈率 <1% 且红队检出 ≥95%；合规区域 ≥2 | M3、R-01 |

## 3. 人力（H1 稳态，按角色，可兼任）

| 角色 | 人数 | 负责 |
|---|---|---|
| 数据层工程（recorder/ingest/export/schema） | 2 | M1、ingest-spec、data-format-contract |
| 策展/感知算法（清洗、伪标签、VLM 标注） | 2–3 | M2、cleaning-algo-selection |
| 训练/评测 | 2 | M3、eval-protocol、training-pipeline |
| 硬件/固件（头戴设备、UMI、遥操作站） | 2 | P0–P2、recorder 固件 |
| 平台/运维/App | 2 | data-platform、Creator App |
| 合规/法务（可外部） | 0.5 | compliance-and-security |
| 运营（Creator 网络、任务库、HITL 审核） | 1 + 审核员 5/千小时·月（curation §9） | index-replica-plan §2 |
| 项目管理 | 0.5 | governance、本文 |

合计核心 ~12 人 + 审核员。

## 4. 预算总盘（12 个月，量级）

| 项 | H0（0–3 月） | H1（3–6 月） | H2（6–12 月） | 备注 |
|---|---|---|---|---|
| Creator 计酬 | $5k | $50k | $500k–1M | 按通过分钟计酬；H2 千人网络 |
| 采集设备 | $5k（手机补贴 + UMI ×2） | $30–60k（EVT 10–50 台 × $600 含 NRE 摊销） | $150–300k（500 台 × $300） | index-replica-plan §1 BOM |
| 本体与遥操作站 | $30–80k（1 台 + Quest 3 + 工控机） | +$100–300k（3–5 台） | 维持 | 取决于本体选型（U-04） |
| 平台（存储/算力/托管） | $3k/月 | $6–8k/月 | $30–80k/月 | data-platform §1.3 |
| 训练算力 | 单卡/云 <$5k | Stage B（S 档）5k–30k GPU·h ≈ $15–100k | Stage B（M 档）3–10 万 H100·h ≈ $100–300k | research-vla-pretraining §5 |
| VLM API | <$1k | $3–5k | $20–50k | 只仲裁分歧样本 |
| HITL 审核 | 内部 | 5 人·月 × 3 | 按入湖量线性 | curation §9 |
| 合规/法务 | $10–20k | $20–40k | $50–100k | 区域数 |
| 人力（12 人） | 按当地薪资另计 | | | |
| **合计（不含人力）** | **≈$70–150k** | **≈$300–650k** | **≈$1.2–2.5M** | |

止损点：H0 末伪标签无仿真收益 → 不投 P1 硬件，转 UMI + robot 轨路线；H1 末单位成本未达 1/3 → 冻结 EVT 扩量（R-02）。

## 5. 复检节奏

- 每月：漏斗、成本、欺诈红队、死信队列。
- 每季度：governance 三表复检（owner 逐条更新状态）、单位经济重算、license 表增量核查。
- 每里程碑：验收矩阵逐条打勾并记录证据（run_id、报告 URI）。
