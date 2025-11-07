import tempfile

import urgap


def test_out_side_urun_dict_is_not_modified_by_kwargs():
    with tempfile.TemporaryDirectory() as tmpdirname:
        urun_dict = urgap.URunDict(
            {
                "parameters": {
                    "triggers_nuttin": 100,
                    "triggers_rerun": 100,
                    "triggers_rerun_-3": 100,
                },
                "unode_parameters": {
                    "record_skipped_runs": True,
                    "storage_base_uri": f"file://{tmpdirname}",
                },
            },
        )
        ufiles = urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        )
        test_node1 = urgap.init_node("TestNode1:1.0.0")
        _ = test_node1.run(ufiles=ufiles, urun_dict=urun_dict, force=True)
        assert urun_dict.unode_parameters.get("force", None) is not True
