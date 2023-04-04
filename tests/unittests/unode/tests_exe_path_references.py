from pathlib import Path



def test_exe_path_points_to_same_location():

    exe_path = unode.construct_exe_path()
    assert exe_path == Path(
    )

    exe_path_2 = unode_2.construct_exe_path()
    assert exe_path == exe_path_2