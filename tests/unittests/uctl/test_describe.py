from click.testing import CliRunner

import urgap

from urgap.uctl.describe import describe_node_ex_id_click, describe_wid_click

runner = CliRunner()


def test_describe_wid_click(caplog, tmp_dir):
    ufiles = (
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        ),
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {"BasicFunctionTestNode:1.1.0": {}},
            "unode_parameters": {
                "record_skipped_runs": True,
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    test_node1 = urgap.init_unode("BasicFunctionTestNode:1.1.0")
    test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    runner.invoke(describe_wid_click, [urun_dict.wid])
    assert "<urgap.umeta.umeta.UMeta object at" in caplog.text
    assert (
        "BasicFunctionTestNode_1.1.0_w4_d751713988987e9331980363e24189ce/3ac34db4765f993a029ba0bbc219a15c"
        in caplog.text
    )


def test_describe_node_ex_id_click(caplog, tmp_dir):
    ufiles = (
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        ),
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {"BasicFunctionTestNode:1.1.0": {}},
            "unode_parameters": {
                "record_skipped_runs": True,
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    test_node1 = urgap.init_unode("BasicFunctionTestNode:1.1.0")
    test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    runner.invoke(
        describe_node_ex_id_click,
        [
            "BasicFunctionTestNode_1.1.0_w4_d751713988987e9331980363e24189ce/3ac34db4765f993a029ba0bbc219a15c",
        ],
    )
    assert "<urgap.umeta.umeta.UMeta object at" in caplog.text
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
        "No History found for given pac_id: BasicFunctionTestNode:1.1.0" in caplog.text
    )