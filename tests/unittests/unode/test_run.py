import pytest

import urgap


def test_run_unode(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "BasicFunctionTestNode:1.3.0": {
                    "-q": "500 < `exp_mz` < 1000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    test_node = urgap.init_unode("BasicFunctionTestNode:1.3.0")
    results = test_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert len(results) == 1


def test_run_unode_no_urd(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
    urun_dict = {
        "parameters": {
            "BasicFunctionTestNode:1.3.0": {
                "-q": "500 < `exp_mz` < 1000",
            },
        },
        "unode_parameters": {
            "storage_base_uri": f"file://{tmp_dir}",
        },
    }
    test_node = urgap.init_unode("BasicFunctionTestNode:1.3.0")
    with pytest.raises(TypeError):
        test_node.run(urun_dict=urun_dict, ufiles=ufiles)