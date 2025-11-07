import tempfile

from pathlib import Path

import urgap


def test_rerun_reason_by_force():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_abcdefg.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    urd = urgap.URunDict({"unode_parameters": {"force": True}})
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_node("filter_csv_1_0_0").META_INFO,
    )
    assert len(ut.evaluate_if_rerun_is_required()) == 1
    assert "Force" in ut.rerun_reasons[0]
    assert "Force" in ut.evaluate_if_rerun_is_required()[0]


def test_rerun_reason_output_files_are_missing():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_abcdefg.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_node("filter_csv_1_0_0").META_INFO,
    )
    assert len(ut.evaluate_if_rerun_is_required()) == 1


def test_rerun_reason_dynamic_output_files_are_less_than_min():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
                f"/sequence_abcdefg.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        urd = urgap.URunDict(
            {"unode_parameters": {"storage_base_uri": f"file://{tmpdirname}"}},
        )
        print("created temporary directory", tmpdirname)

        ut = urgap.UTrace(
            urun_dict=urd,
            input_files=input_files,
            unode_meta=urgap.init_node("TestNode4:1.0.0").META_INFO,
        )
        dynout_ufile = ut.output_files[0]
        base, extension = dynout_ufile.object_name.split("_1_of_N")
        # Creating one correct and one wrong output
        dynout_filename = Path(f"{tmpdirname}/{base}_1_of_2{extension}")
        wrong_dynout_filename = Path(f"{tmpdirname}/{base}_1_of_2.just.wrong")

        dynout_filename.parent.mkdir(parents=True, exist_ok=True)
        dynout_filename.touch()
        wrong_dynout_filename.touch()

        ut._remote_output_files = None
        assert len(ut.remote_output_files) == 1
        rerun_reasons = ut.evaluate_if_rerun_is_required()
        assert "Not all dynamic files were written" in rerun_reasons[0]
