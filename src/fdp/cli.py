"""fdp 命令行入口。子命令与管线层一一对应（docs/architecture.md §7）。"""

import typer

app = typer.Typer(help="Humanoid data pipeline: record → ingest → curate → export → viz")


@app.command()
def record() -> None:
    """采集：遥操作/传感器流写入 MCAP（M1，未实现）。"""
    raise typer.Exit("not implemented: fdp.recorder")


@app.command()
def ingest() -> None:
    """入湖：校验、时间对齐、转码（M1，未实现）。"""
    raise typer.Exit("not implemented: fdp.ingest")


@app.command()
def curate() -> None:
    """策展：质量门/去重/再平衡/VLM 标注（M2，未实现）。"""
    raise typer.Exit("not implemented: fdp.curation")


@app.command()
def export() -> None:
    """导出 LeRobotDataset v3（M1，未实现）。"""
    raise typer.Exit("not implemented: fdp.export")


@app.command()
def viz() -> None:
    """rerun 可视化检视 episode（M1，未实现）。"""
    raise typer.Exit("not implemented: fdp.viz")


def main() -> None:
    app()
