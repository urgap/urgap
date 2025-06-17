import tempfile



def test_out_side_urun_dict_is_not_modified_by_kwargs():
    with tempfile.TemporaryDirectory() as tmpdirname:
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
            [
                    f"test_node_data/test.txt",
                ),
            ],
        )
        _ = test_node1.run(ufiles=ufiles, urun_dict=urun_dict, force=True)
        assert urun_dict.unode_parameters.get("force", None) is not True