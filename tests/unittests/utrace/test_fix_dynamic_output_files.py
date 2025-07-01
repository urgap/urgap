import urgap


def test_fix_dynamic_output_file_names():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.test.TEST_FILE2}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    urd = urgap.URunDict()

    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode2:1.0.0").META_INFO,
    )
    assert len(ut.output_files) == 4
    ut.extend_output_files_by_uftype(urgap.uftypes.test.TEST_FILE1)
    assert len(ut.output_files) == 5
    idx_groups = ut.output_files.get_index_groups_by_uftypes()
    ut.output_files.complete_file_counts()
    assert (
        "1_of_1"
        in ut.output_files[idx_groups[urgap.uftypes.test.TEST_FILE1][0]].object_name
    )