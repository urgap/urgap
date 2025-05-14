from click.testing import CliRunner



runner = CliRunner()


def test_describe_wid_click(caplog, tmp_dir):
    ufiles = (
            [
                    f"test_node_data/test.txt",
                ),
        ),
    )
        {
            "parameters": {"BasicFunctionTestNode:1.1.0": {}},
            "unode_parameters": {
                "record_skipped_runs": True,
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    runner.invoke(describe_wid_click, [urun_dict.wid])
    assert (
        "BasicFunctionTestNode_1.1.0_w4_d751713988987e9331980363e24189ce/3ac34db4765f993a029ba0bbc219a15c"
        in caplog.text
    )


def test_describe_node_ex_id_click(caplog, tmp_dir):
    ufiles = (
            [
                    f"test_node_data/test.txt",
                ),
        ),
    )
        {
            "parameters": {"BasicFunctionTestNode:1.1.0": {}},
            "unode_parameters": {
                "record_skipped_runs": True,
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    runner.invoke(
        describe_node_ex_id_click,
        [
        ],
    )
    assert (
        "BasicFunctionTestNode_1.1.0_w4_d751713988987e9331980363e24189ce/3ac34db4765f993a029ba0bbc219a15c"
        in caplog.text
    )


def test_describe_wid_doesnt_exist_click(caplog):
    runner.invoke(describe_wid_click, ["test_wid"])
    assert "No History found for given wid: test_wid" in caplog.text


def test_describe_node_ex_id_doesnt_exist_click(caplog):
    runner.invoke(describe_node_ex_id_click, ["BasicFunctionTestNode:1.1.0"])
    assert (
    )