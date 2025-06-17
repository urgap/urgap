

def test_fix_dynamic_output_file_names():
        [
                f"/sequence_defghij.csv",
            ),
        ],
    )

        urun_dict=urd,
        input_files=input_files,
    )
    assert len(ut.output_files) == 4
    assert len(ut.output_files) == 5
    idx_groups = ut.output_files.get_index_groups_by_uftypes()
    ut.output_files.complete_file_counts()
    assert (
        "1_of_1"
    )