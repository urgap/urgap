import pytest

from click.testing import CliRunner

from urgap.uctl.uctl import cli

runner = CliRunner()


def test_cli_main_help():
    """Test that the main CLI shows help text and lists all commands."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ["set", "show", "describe", "run", "info", "upload"]:
        assert cmd in result.output
    assert "Start the urgap command-line interface" in result.output


@pytest.mark.parametrize(
    "subcommand",
    [
        "set",
        "show",
        "describe",
        "run",
        "info",
        "upload",
    ],
)
def test_cli_subcommand_help(subcommand):
    """Test that each subcommand shows help text."""
    result = runner.invoke(cli, [subcommand, "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output or "Show this message and exit." in result.output


def test_cli_unknown_command():
    """Test that unknown commands show an error."""
    result = runner.invoke(cli, ["doesnotexist"])
    assert result.exit_code != 0
    assert "No such command" in result.output
