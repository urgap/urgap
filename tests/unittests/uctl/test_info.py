from click.testing import CliRunner

import urgap

runner = CliRunner()


def test_info_unodes():
    from urgap.uctl.info import info_unodes_click

    wrappers = urgap.instances.unode_manager.wrapper_lookup.keys()
    result = runner.invoke(info_unodes_click)
    for wrapper in wrappers:
        if "TestNode" in wrapper:
            continue
        assert wrapper in result.stdout
        assert "ERROR" not in result.stdout


def test_info_umeta():
    from urgap.uctl.info import info_umeta_click

    umeta = urgap.config["umeta"]
    result = runner.invoke(info_umeta_click)
    assert umeta in result.stdout
    assert "Number of unode_exe_details Documents:" in result.stdout
    assert "Number of history Documents:" in result.stdout
    assert "Number of input links Documents:" in result.stdout
    assert "Number of output links Documents:" in result.stdout