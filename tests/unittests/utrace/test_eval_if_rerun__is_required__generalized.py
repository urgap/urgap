import tempfile
from pathlib import Path



def test_rerun_reason_by_force():
        [
            ),
            ),
    )
        urun_dict=urd,
    )
    assert len(ut.evaluate_if_rerun_is_required()) == 1
    assert "Force" in ut.rerun_reasons[0]
    assert "Force" in ut.evaluate_if_rerun_is_required()[0]


def test_rerun_reason_output_files_are_missing():
        [
            ),
            ),
    )
        urun_dict=urd,
    )
    assert len(ut.evaluate_if_rerun_is_required()) == 1


def test_rerun_reason_dynamic_output_files_are_less_than_min():
        [
            ),
            ),
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        )
        print("created temporary directory", tmpdirname)

            urun_dict=urd,
        )
        dynout_ufile = ut.output_files[0]
        base, extension = dynout_ufile.object_name.split("_1_of_N")
        # Creating one correct and one wrong output
        dynout_filename = Path(f"{tmpdirname}/{base}_1_of_2{extension}")
        wrong_dynout_filename = Path(f"{tmpdirname}/{base}_1_of_2.just.wrong")

        dynout_filename.parent.mkdir(parents=True, exist_ok=True)
        dynout_filename.touch()
        wrong_dynout_filename.touch()

        assert len(ut.remote_output_files) == 1
        rerun_reasons = ut.evaluate_if_rerun_is_required()
        assert "Not all dynamic files were written" in rerun_reasons[0]