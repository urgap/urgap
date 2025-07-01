import urgap


def test_extend_output_file_list():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
                f"/sequence_abcdefg.csv",
            ),
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
        unode_meta=urgap.init_node("TestNode4:1.0.0").META_INFO,
    )
    assert len(ut.output_files) == 1


def test_extend_output_file_list_increase_one():
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
    ut.extend_output_files_by_uftype(urgap.uftypes.test.TEST_FILE2)
    assert len(ut.output_files) == 6


def test_extend_output_file_list_does_not_increase_over_max():
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
    ut.extend_output_files_by_uftype(urgap.uftypes.test.TEST_FILE3)
    assert len(ut.output_files) == 4