import pytest

import urgap


def test__test_command():
    um = urgap.UNodeManager()
    is_available = um._test_command(command_list=["ls", "-l"])
    assert is_available is True


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