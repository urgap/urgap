from pathlib import Path



def test_exe_path_points_to_same_location():

    exe_path = unode.construct_exe_path()
    assert exe_path == Path(
    )

    exe_path_2 = unode_2.construct_exe_path()
    assert exe_path == exe_path_2


def test_exe_works_in_both_cases():
        [
    )
    result_6 = test_node6.run(ufiles=ufiles, urun_dict=urun_dict, force=True)
    result_7 = test_node7.run(ufiles=ufiles, urun_dict=urun_dict, force=True)
    assert len(result_6) == len(result_7) == 1
    assert result_6[0].path.read_text().startswith("Dave, ")
    assert result_7[0].path.read_text().strip().endswith("Goodbye.")