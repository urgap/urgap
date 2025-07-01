from pathlib import Path

import urgap


def test_exe_path_points_to_same_location():
    unode = urgap.init_node("TestNode6:1.0.0")

    exe_path = unode.construct_exe_path()
    assert exe_path == Path(
        f"{urgap.home}/resources/platform_independent/arc_independent/TestNode6:1.0.0"
        f"/TestNode6:1.0.0.py",
    )

    unode_2 = urgap.init_node("TestNode7:1.0.0")
    exe_path_2 = unode_2.construct_exe_path()
    assert exe_path == exe_path_2


def test_exe_works_in_both_cases():
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data#"
                f"test_node_data/test.txt?uftype={urgap.uftypes.test.TEST_FILE2}",
            ),
        ],
    )
    urun_dict = urgap.URunDict()
    test_node6 = urgap.init_node("TestNode6:1.0.0")
    test_node7 = urgap.init_node("TestNode7:1.0.0")
    result_6 = test_node6.run(ufiles=ufiles, urun_dict=urun_dict, force=True)
    result_7 = test_node7.run(ufiles=ufiles, urun_dict=urun_dict, force=True)
    assert len(result_6) == len(result_7) == 1
    assert result_6[0].path.read_text().startswith("Dave, ")
    assert result_7[0].path.read_text().strip().endswith("Goodbye.")