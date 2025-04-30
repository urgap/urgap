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
    runner.invoke(describe_wid_click, ["test_wid"])


    runner.invoke(describe_node_ex_id_click, ["BasicFunctionTestNode:1.1.0"])