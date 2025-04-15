import pytest



def test_unode_construct_exe_path():
    _path = unode.construct_exe_path()
    assert (
        _path
        / "resources"
        / "TestNodes"
        / "TestNode1"
        / "1_0_0"
        / "test_resource_1.py"
    )


def test_unode_construct_exe_path_latest():
    with pytest.raises(RuntimeError):
        _path = unode.construct_exe_path()