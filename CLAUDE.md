# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

对标 Figure（Helix 02 + Figure 03 + Index）的开源人形机器人**数据管线与数据采集工具**。总设计见 [docs/architecture.md](docs/architecture.md)——改动任何管线层之前先读它；全部文档的索引与按角色阅读路径见 [docs/README.md](docs/README.md)；风险登记、未决决策、自报数字登记见 [docs/governance.md](docs/governance.md)。

## 常用命令

uv 管理一切（Python 3.12）：

```bash
uv sync                 # 安装/同步依赖
uv run pytest           # 全部测试
uv run pytest tests/test_schema.py -k test_name   # 单个测试
uv run ruff check src tests    # lint
uv run ruff format src tests   # 格式化
uv run fdp --help       # CLI 入口
uv run python scripts/check_docs_links.py   # docs 相对链接/图片路径与禁用词扫描（CI 也跑）
```

## 架构（大图）

数据流五层，`src/fdp/` 子包与之一一对应，CLI 子命令按层对应（`record`/`ingest`/`curate`/`export`/`viz`，动词形式，与子包名不完全相同）：

```
recorder(采集,MCAP) → ingest(入湖:校验/对齐/转码) → curation(策展) → export(LeRobotDataset v3) → viz(rerun)
```

能力→模块→CLI→里程碑的完整映射表见 docs/architecture.md §7。

贯穿性设计决策（偏离前必须先更新 docs/architecture.md）：

1. **双格式**：机上采集/原始数据用 MCAP（append-only 耐崩、多流单文件）；训练/发布态用 LeRobotDataset v3（parquet+mp4、流式）。二者间由 `export` 层转换，不引入第三种持久化格式。
2. **四轨同 schema**：robot（遥操作/车队，含动作真值）、human（第一视角视频，无动作标签）、device（UMI/Data Hands 式手持采集，硬件动作真值）、sim（仿真 rollout）四条 ingest 轨共用 `fdp/schema.py` 的 EpisodeMeta，用 `track` 字段区分；采集方式是组合不是单选，新增采集形态=新增 track 值，不新增 schema。所有模态可空（mask），schema 带版本号，新增传感器不得破坏旧数据可读性。
3. **分层采样率**：视觉流 ~10-30 Hz（对齐 VLM/S2 消费）、状态/动作流 100-200 Hz（对齐动作专家/S1 消费），统一时间戳（ns）对齐，不做全局重采样到单一频率。**豁免**：device 轨（UMI 等手持/穿戴设备）的动作流以传感器原生频率入湖（≥50Hz，如 VIO 位姿 60Hz），`rate_hz` 如实记录，export 不做上采；训练取帧时对信号流线性插值（docs/curation-pipeline.md §5）。时间戳语义与同步误差预算见 docs/architecture.md §8。
4. **策展五阶段**（curation 层，对标 Index）：自动质量门 → 欺诈/来源审计 → embedding 去重 → 多样性再平衡 → VLM 分层标注（任务级+子任务级指令，事后反推式）。QC 三级：L1 运动学过滤 / L2 统计过滤 / L3 VLM 语义审计。详细实施规范（episode 状态机、各门方法与阈值原则、分割/伪标签/打包）见 docs/curation-pipeline.md；清洗是标记不是删除，raw 永存（隐私脱敏除外），阈值改动必须走消融裁决。
5. **视频编码**：机上 h264 硬编，入湖转 AV1（svt-av1）+ `yuv420p`（yuv444p 会导致浏览器/可视化不可解码），解码用 torchcodec。
6. **质量优先于吞吐**：Figure 用 8 小时精策划数据即出可用策略。数据质量评估/过滤模块的优先级高于采集吞吐优化；缩放消融切分器（按小时/任务/operator_id）是数据集层内建能力，不是事后脚本。
7. **训练层设计保守、数据层承载创新**：模型决策只抄 ≥2 家独立验证的共识（VLM 骨干+流匹配头、槽位向量+掩码、相机系增量动作、两段式动作课程），不自研骨干；数据配方（configs/mixtures/*.yaml）是版本化一等公民，哈希入 lineage。详见 docs/training-pipeline.md。

## 当前阶段

M1（采集与格式）：recorder/ingest/export/viz 均为占位 stub，schema.py 为 0.2（含 0.1→0.2 读侧迁移 `migrate()`，冻结样本 tests/fixtures/episode_v0_1.json 必须永远可读）。工程路线图 M1→M3 见 docs/architecture.md §7"落地阶段"；Index 复刻硬件/平台线用 H0/H1/H2（docs/index-replica-plan.md §7），采集硬件成熟度用 P0/P1/P2，三套前缀不混用。实现新模块时先接 CLI 子命令与测试，再填实现；数据格式改动先改 docs/data-format-contract.md 再改 schema.py。

## 约定

- `data/` 不进 git（.gitignore 已配），采集/导出产物一律落在这里；`configs/` 存 yaml 配方与阈值（`configs/mixtures/` 为训练配方），改动配方=新版本，不覆盖旧文件。
- 涉及 Figure 或其他公司的事实性宣称（数字、能力）时引用 docs/research-*.md 的已核查条目，不凭记忆写；引用他家数字必须标注来源属性（官方确认 / 第三方 / 公司自报 ⚠️），依赖自报数字的设计决策登记进 docs/governance.md 的 D 表。
- 引入任何模型/算法依赖前先查 docs/cleaning-algo-selection.md 的 license 列：非商用许可（DOVER/FAST-VQA/pyiqa 等）只允许出现在研究分支，⚠️待核查项不得进入默认路径。
- 隐私：清洗是标记不是删除，raw 永存的唯一例外是隐私脱敏与合法删除请求（docs/compliance-and-security.md）。
- 提交信息与文档日期用绝对日期（YYYY-MM-DD）。
