import pytest

import urgap


def test_unode_construct_exe_path():
    unode = urgap.init_node("TestNode1:1.0.0")
    _path = unode.construct_exe_path()
    assert (
        _path
        == urgap.home
        / "resources"
        / "TestNodes"
        / "TestNode1"
        / "1_0_0"
        / "test_resource_1.py"
    )


def test_unode_construct_exe_path_latest():
    unode = urgap.init_node("TestNode1:latest")
    with pytest.raises(RuntimeError):
        _path = unode.construct_exe_path()
