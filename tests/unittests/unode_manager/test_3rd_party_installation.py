import pytest

import urgap

from urgap.unode_manager import UNodeManager


def test__test_command():
    um = urgap.UNodeManager()
    is_available = um._test_command(command_list=["ls", "-l"])
    assert is_available is True


def test_init_unode_logs_suggestions(caplog):
    import urgap

    um = urgap.UNodeManager()

    with caplog.at_level("DEBUG"):
        result = um.init_unode("NonExistentNode")

    assert result is None
    assert any("Did you mean" in rec.message for rec in caplog.records) or any(
        "shorten the name" in rec.message for rec in caplog.records
    )


def test_unknown_dependency_logs_warning(caplog):
    from urgap.unode_manager import UNodeManager

    um = UNodeManager()
    requirements = {"other_dependencies": ["fake_dep"]}
    availabilities = []

    with caplog.at_level("WARNING"):
        um._check_other_dependencies(
            availabilities=availabilities, requirements=requirements, unode="TestNode"
        )

    assert "Wrapper TestNode contains requirements fake_dep" in caplog.text
    assert availabilities == []


def test_meta_info_fallback_to_instance(tmp_path, monkeypatch):
    dummy_file = tmp_path / "dummy_unode.py"
    dummy_file.write_text("""
class DummyClass:
    def __init__(self):
        self.META_INFO = {"name": "dummy_node", "engine_type": ["test_engine"]}
""")

    monkeypatch.setattr(urgap, "package_dir", tmp_path)

    um = UNodeManager()

    lookup = {}
    um._add_to_lookup(lookup=lookup, wrapper=dummy_file)

    assert any("dummy_node" in k for k in lookup)


def test__test_command_with_regex():
    um = urgap.UNodeManager()

    is_available = um._test_command(
        command_list=["echo", "hello123"], regex_pattern=r"hello\d+"
    )
    assert is_available is True


def test__check_for_module():
    um = urgap.UNodeManager()
    no_version = um._check_for_module("definitely_no_module")
    assert no_version is None
    pandas_version = um._check_for_module("pandas")
    assert pandas_version is not None


def test__test_command_not_available():
    um = urgap.UNodeManager()
    is_available = um._test_command(command_list=["ls", "", "-"])
    # having space in the list will always crash....
    assert is_available is False


def test_has_all_required_third_party_installs_without_init():
    test_node = urgap.init_node("TestNode4:1.0.0")
    assert test_node.has_all_required_installations() is True
    urgap.instances.unode_manager["node_availability_lookup"] = {}
    assert test_node.has_all_required_installations() is True


def test__check_for_module():
    um = urgap.UNodeManager()
    no_version = um._check_for_module("definitely_no_module")
    assert no_version is None
    pandas_version = um._check_for_module("pandas")
    assert pandas_version is not None


@pytest.mark.parametrize(
    "requirements",
    [
        ({"python_packages": ["pandas"]}, True),
        ({"python_packages": ["pandas<0.0.3", "pandas>0.0.3"]}, False),
        ({"python_packages": ["no_package_for_sure"]}, False),
        (
            {"python_packages": ["pandas>=0.0.3", "plotly", "networkx", "click>=1.2"]},
            True,
        ),
    ],
)
def test_check_pypackage_requirements(requirements):
    reqs, expected = requirements
    um = urgap.UNodeManager()
    is_available = um.check_requirements(requirements=reqs)
    assert is_available is expected