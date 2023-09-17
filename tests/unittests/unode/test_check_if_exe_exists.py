

def test_unode_check_if_all_exe_exist():
    assert output is True


def test_unode_check_if_all_exe_exist_wrong_exe():
    output = unode.check_if_all_exe_exist(["tandem"])
    assert output is False