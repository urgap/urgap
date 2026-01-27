import urgap


def test_unode_check_if_all_exe_exist():
    unode = urgap.init_node("FilterTabularToCSV:1.0.0")
    output = unode.check_if_all_exe_exist(["filter_tabular.py"])
    assert output is True


def test_unode_check_if_all_exe_exist_wrong_exe():
    unode = urgap.init_node("omssa_2_1_9")
    output = unode.check_if_all_exe_exist(["tandem"])
    assert output is False
