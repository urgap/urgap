from click.testing import CliRunner


runner = CliRunner()


def test_info_unodes():

    result = runner.invoke(info_unodes_click)
    for wrapper in wrappers:
        if "TestNode" in wrapper:
            continue
        assert wrapper in result.stdout
        assert "ERROR" not in result.stdout


def test_info_umeta():

    result = runner.invoke(info_umeta_click)
    assert umeta in result.stdout