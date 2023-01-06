

def test_extend_output_file_list():
        [
            ),
            ),
    )

        urun_dict=urd,
        input_files=input_files,
    )
    assert len(ut.output_files) == 1


def test_extend_output_file_list_increase_one():
        [
            ),
    )

        urun_dict=urd,
        input_files=input_files,
    )
    assert len(ut.output_files) == 4
    assert len(ut.output_files) == 5
    assert len(ut.output_files) == 6


def test_extend_output_file_list_does_not_increase_over_max():
        [
            ),
    )

        urun_dict=urd,
        input_files=input_files,
    )
    assert len(ut.output_files) == 4
    assert len(ut.output_files) == 4