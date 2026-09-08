# 数据平台：容量/成本模型 · 组件选型 · lineage · 可观测性

> 2026-09-08。承接 [index-replica-plan.md](index-replica-plan.md) §3 的框图，把"对象存储三区 / Postgres / 向量库 / 队列 DAG"从名词变成决策。所有成本为 2026 年公有云挂牌价量级估算，用于决策不用于报价；每季度按实际账单重算（governance R-02）。

## 1. 容量与成本模型

### 1.1 码率假设

| 流 | 参数 | 码率 | GB/小时 |
|---|---|---|---|
| 主视频（机上 h264/h265，存档流） | 1440p60 或 4K30 | 20–30 Mbps | 9–13.5 |
| 入湖后 AV1（存档，同分辨率） | svt-av1 preset 6, CRF 30 | 8–12 Mbps | 3.6–5.4 |
| 训练分辨率 AV1（448p–720p） | | 1–3 Mbps | 0.45–1.35 |
| 预览流 | 320p | 0.3 Mbps | 0.14 |
| 信号流（100–200 Hz × ~100 维 float32 + IMU） | | <1 Mbps | ~0.3 |
| 中间产物（embedding、关键点、光流缓存） | | | 0.5–2（光流最大，可按需重算） |

单路相机口径；robot 轨 3 路相机 ×，human/device 轨 1–2 路。

### 1.2 存储量级（按每月入湖可用数据小时数 H，含未通过策展的原始上传 ≈3H）

| 阶段 | H | raw（AV1 存档，3H × ~5 GB） | curated + training | 中间产物 | 累计 12 个月 |
|---|---|---|---|---|---|
| H0 | 100 h/月 | 1.5 TB/月 | 0.2 TB/月 | 0.3 TB/月 | ~25 TB |
| H1 | 1,000 h/月 | 15 TB/月 | 2 TB/月 | 3 TB/月 | ~250 TB |
| H2 | 10,000 h/月 | 150 TB/月 | 20 TB/月 | 30 TB/月 | ~2.5 PB |

"raw 永存"意味着 raw 区只增不减。**分层存储**：raw 入湖 30 天后转冷存（≈$1–4/TB·月），curated/training 热存（≈$20/TB·月），中间产物可重算的 90 天后删除（不算违反 raw 永存）。

### 1.3 月费估算（H1 口径，1,000 h/月）

| 项 | 估算 |
|---|---|
| 存储：热 ~10 TB + 冷累计 ~150 TB（年中） | $200 + $450 ≈ $0.7k |
| 出口带宽（训练读 training 区，同区域近零；跨区 ≤10 TB） | ≤$1k |
| 策展算力：转码（AV1 硬编 ~0.1 GPU·h/h）、感知模型（手部/SLAM/光流 ~0.5 GPU·h/h）、VLM（本地 ~0.2 GPU·h/h + API 分歧样本 <5%） | ~0.8 GPU·h × 3,000 h 原始 ≈ 2,400 GPU·h ≈ $3–5k |
| 元数据库/向量库/队列（托管） | $0.5–1k |
| 合计 | **≈$6–8k/月**，即每可用小时 $6–8 平台成本（不含计酬与设备） |

H2 线性外推约 $60–80k/月；这一项进 program-plan 预算并与 R-02 止损阈值联动。

## 2. 组件选型

| 组件 | 选择 | 备选 | 理由 |
|---|---|---|---|
| 对象存储 | S3 兼容（公有云 S3/OSS，或自建 MinIO 起步） | — | 三区 raw/curated/training 用 bucket + 前缀 + 生命周期规则实现分层 |
| 元数据库 | **PostgreSQL**（episode/session/device/operator/lineage 表） | — | 关系查询、事务、JSONB 存 EpisodeMeta 扩展 |
| 向量库 | **pgvector**（H0/H1，≤1e7 向量） → Milvus/Qdrant（H2） | — | 起步不引入新系统 |
| DAG / 队列 | **Prefect 或 Dagster**（Python 原生，资产化 lineage） + Redis/RabbitMQ 队列 | Airflow | 策展阶段=资产，幂等重放、失败死信（curation §6） |
| GPU 调度 | Kubernetes + 队列（H1 起）；H0 单机 | Ray | 批处理为主，无需在线服务 |
| 视频转码 | ffmpeg + svt-av1，硬编（NVENC/VideoToolbox）优先 | | research-opensource §4 |
| lineage / 数据版本 | **自建表 + 数据集快照 manifest**（§3）；训练分片用 LeRobot 数据集版本 tag | DVC / LakeFS | DVC 对 PB 级视频不合适；LakeFS 可在 H2 评估 |
| 检索/演示库 | pgvector + 元数据过滤 | | 演示库 = 带 embedding 的 clip 表 |
| 可视化 | rerun（episode 检视）+ Foxglove（MCAP 调试）+ Grafana（运营指标） | | |

## 3. lineage 表结构

```
episodes(episode_id PK, session_id, track, source, state, meta JSONB, storage_uri, content_hash, created_at)
sessions(session_id PK, operator_id, device_id, robot_model, scene_id, started_at, calibration_ref, firmware_version)
devices(device_id PK, kind, camera_map JSONB, calibration_ref, firmware_version, region)
operators(operator_id PK, kind[operator|creator], region, reputation, consent_ref)
artifacts(artifact_id PK, episode_id FK, stage, kind[embedding|keypoints|flow|transcode|label|transform], model_name, model_version, weight_hash | api_version, config_hash, uri, created_at)
decisions(decision_id PK, episode_id FK, stage, verdict[pass|flag|reject], flags[], score, config_hash, model_ref, decided_at)
datasets(dataset_version PK, manifest_uri, mixture_config_hash, split_version, created_at)
dataset_episodes(dataset_version FK, episode_id FK, shard, split)
training_runs(run_id PK, dataset_version FK, mixture_config_hash, code_commit, checkpoint_uri, eval_report_uri)
deletions(request_id PK, subject[operator_id|episode_id], requested_at, propagated_to[] , completed_at)
```

规则：每个策展阶段写一行 `decisions` 与零到多行 `artifacts`；模型升级 = 新 `model_version`，历史 decision 不改；`datasets.manifest_uri` 指向冻结的 episode 列表与哈希；删除请求沿 `dataset_episodes → training_runs` 查出受影响模型并记录（compliance §4）。

## 4. 可观测性与 SLO

| 指标 | SLO | 告警 |
|---|---|---|
| 上传成功率（分片级） | ≥99% | <97% 15 分钟 |
| ingest 延迟（上传完成 → ingested） | P95 ≤ 1 小时 | >4 小时 |
| 策展 DAG 吞吐 | ≥ 当日入湖量 | 积压 >24 小时 |
| 各门通过率漏斗 | 周报；单门通过率周环比变化 >20% 触发人工检查（可能是阈值/模型漂移） | |
| 死信队列 | 0 积压 >24 小时 | |
| VLM API 错误率 / 延迟 | <1% / P95 ≤10 s；超限自动切本地模型 | |
| 存储增长 vs 预算 | 月度 | 超预算 20% |
| 欺诈红队植入检出率 | ≥95%（每月投放已知欺诈样本集） | <90% |

日志：每个 worker 结构化日志带 `episode_id` 与 `stage`，可从任一 episode 追到全部处理记录。

## 5. 反欺诈 ground truth

红队测试集：每月由平台方自己制作 ≥100 条已知欺诈样本（翻拍、重复上传改名、时空不一致、静止摆拍），混入正常流量；检出率即漏检率的度量（governance R-05）。样本与结果进 `decisions`，不进训练集。
