"""fdp 命令行入口。子命令与管线层按层对应（docs/architecture.md §7）。"""

import typer

app = typer.Typer(
    help="Humanoid data pipeline: record → ingest → curate → export → viz"
)


def _not_implemented(module: str) -> None:
    typer.echo(f"not implemented: {module}", err=True)
    raise typer.Exit(code=1)


@app.command()
def record() -> None:
    """采集：遥操作/传感器流写入 MCAP（M1，未实现）。"""
    _not_implemented("fdp.recorder")


@app.command()
def ingest() -> None:
    """入湖：校验、时间对齐、转码（M1，未实现）。"""
    _not_implemented("fdp.ingest")


@app.command()
def curate() -> None:
    """策展：质量门/去重/再平衡/VLM 标注（M2，未实现）。"""
    _not_implemented("fdp.curation")


@app.command()
def export() -> None:
    """导出 LeRobotDataset v3（M1，未实现）。"""
    _not_implemented("fdp.export")


@app.command()
def viz() -> None:
    """rerun 可视化检视 episode（M1，未实现）。"""
    _not_implemented("fdp.viz")


def main() -> None:
    app()
