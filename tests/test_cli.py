from typer.testing import CliRunner

from fdp.cli import app

runner = CliRunner()


def test_help_lists_all_layers():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("record", "ingest", "curate", "export", "viz"):
        assert cmd in result.output


def test_stub_commands_exit_nonzero_with_message():
    for cmd, module in (
        ("record", "fdp.recorder"),
        ("ingest", "fdp.ingest"),
        ("curate", "fdp.curation"),
        ("export", "fdp.export"),
        ("viz", "fdp.viz"),
    ):
        result = runner.invoke(app, [cmd])
        assert result.exit_code == 1, cmd
        assert f"not implemented: {module}" in result.output
