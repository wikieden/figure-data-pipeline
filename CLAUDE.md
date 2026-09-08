# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

对标 Figure（Helix 02 + Figure 03 + Index）的开源人形机器人**数据管线与数据采集工具**。总设计见 [docs/architecture.md](docs/architecture.md)——改动任何管线层之前先读它；调研依据见 docs/research-figure.md 与 docs/research-opensource.md。

## 常用命令

uv 管理一切（Python 3.12）：

```bash
uv sync                 # 安装/同步依赖
uv run pytest           # 全部测试
uv run pytest tests/test_schema.py -k test_name   # 单个测试
uv run ruff check src tests    # lint
uv run ruff format src tests   # 格式化
uv run fdp --help       # CLI 入口
```

## 架构（大图）

数据流五层，`src/fdp/` 子包与之一一对应，CLI 子命令同名：

```
recorder(采集,MCAP) → ingest(入湖:校验/对齐/转码) → curation(策展) → export(LeRobotDataset v3) → viz(rerun)
```

贯穿性设计决策（偏离前必须先更新 docs/architecture.md）：

1. **双格式**：机上采集/原始数据用 MCAP（append-only 耐崩、多流单文件）；训练/发布态用 LeRobotDataset v3（parquet+mp4、流式）。二者间由 `export` 层转换，不引入第三种持久化格式。
2. **四轨同 schema**：robot（遥操作/车队，含动作真值）、human（第一视角视频，无动作标签）、device（UMI/Data Hands 式手持采集，硬件动作真值）、sim（仿真 rollout）四条 ingest 轨共用 `fdp/schema.py` 的 EpisodeMeta，用 `track` 字段区分；采集方式是组合不是单选，新增采集形态=新增 track 值，不新增 schema。所有模态可空（mask），schema 带版本号，新增传感器不得破坏旧数据可读性。
3. **分层采样率**：视觉流 ~10-30 Hz（对齐 VLM/S2 消费）、状态/动作流 100-200 Hz（对齐动作专家/S1 消费），统一时间戳（ns）对齐，不做全局重采样到单一频率。
4. **策展五阶段**（curation 层，对标 Index）：自动质量门 → 欺诈/来源审计 → embedding 去重 → 多样性再平衡 → VLM 分层标注（任务级+子任务级指令，事后反推式）。QC 三级：L1 运动学过滤 / L2 统计过滤 / L3 VLM 语义审计。详细实施规范（episode 状态机、各门方法与阈值原则、分割/伪标签/打包）见 docs/curation-pipeline.md；清洗是标记不是删除，raw 永存（隐私脱敏除外），阈值改动必须走消融裁决。
5. **视频编码**：机上 h264 硬编，入湖转 AV1（svt-av1）+ `yuv420p`（yuv444p 会导致浏览器/可视化不可解码），解码用 torchcodec。
6. **质量优先于吞吐**：Figure 用 8 小时精策划数据即出可用策略。数据质量评估/过滤模块的优先级高于采集吞吐优化；缩放消融切分器（按小时/任务/operator_id）是数据集层内建能力，不是事后脚本。
7. **训练层设计保守、数据层承载创新**：模型决策只抄 ≥2 家独立验证的共识（VLM 骨干+流匹配头、槽位向量+掩码、相机系增量动作、两段式动作课程），不自研骨干；数据配方（configs/mixtures/*.yaml）是版本化一等公民，哈希入 lineage。详见 docs/training-pipeline.md。

## 当前阶段

M1（采集与格式）：recorder/ingest/export/viz 均为占位 stub，schema.py 已定型为起点。路线图 M1→M3 见 docs/architecture.md §7。实现新模块时先接 CLI 子命令与测试，再填实现。

## 约定

- `data/` 不进 git（.gitignore 已配），采集/导出产物一律落在这里。
- 涉及 Figure 事实性宣称（数字、能力）时引用 docs/research-*.md 的已核查条目，不凭记忆写；该目录区分了官方确认与第三方推断。
