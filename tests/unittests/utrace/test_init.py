import urgap


def test_init_right_number_of_output_files():
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

    urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta={
            "name": "dummy_umets",
            "wrapper_version": {"major": 7},
            "input_uftypes": {
                urgap.uftypes.test.TEST_FILE2: {"min": 1, "max": 1},
            },
            "output_uftypes": {
                urgap.uftypes.test.TEST_FILE4: {"min": 0, "max": -1},
            },
        },
    )
    urgap.UMeta(io="mongodb")