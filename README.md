# figure-data-pipeline (fdp)

对标 Figure（Helix 02 · Figure 03 · Index）的开源人形机器人数据管线与采集工具。

- 文档索引与阅读路径：[docs/README.md](docs/README.md)
- 总体架构：[docs/architecture.md](docs/architecture.md)
- 风险 / 未决决策 / 自报数字登记：[docs/governance.md](docs/governance.md)

```bash
uv sync && uv run fdp --help
```

管线：`record`(MCAP 采集) → `ingest`(校验/对齐/转码) → `curate`(五阶段策展) → `export`(LeRobotDataset v3) → `viz`(rerun)。当前处于 M1 阶段（采集与格式），除 schema 外均为骨架。
