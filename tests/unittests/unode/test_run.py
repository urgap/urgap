import pytest



def test_run_unode(tmp_dir):
        [
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
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
    results = test_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert len(results) == 1


def test_run_unode_no_urd(tmp_dir):
        [
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
    with pytest.raises(TypeError):
        test_node.run(urun_dict=urun_dict, ufiles=ufiles)