import os

import pytest

import urgap


def test_unode_delete_tmp_file():
    test_node = urgap.init_node("TestNode1:1.0.0")
    tmp_file = urgap._test_folder / "data" / "tmp.file"
    with open(tmp_file, "w") as fin:
        fin.write("This is gonna be deleted")
    assert tmp_file.exists() is True
    test_node.tmp_files.append(str(tmp_file))
    test_node.delete_tmp_files()

    assert tmp_file.exists() is False


def test_unode_delete_tmp_dir():
    test_node = urgap.init_node("TestNode1:1.0.0")
    tmp_dir = urgap._test_folder / "data" / "tmp_dir"
    tmp_dir2 = urgap._test_folder / "data" / "tmp_dir2"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    os.symlink(tmp_dir, tmp_dir2)
    assert tmp_dir.exists() is True
    assert tmp_dir2.exists() is True
    test_node.tmp_files.extend([tmp_dir2, tmp_dir])
    test_node.delete_tmp_files()
    assert tmp_dir.exists() is False
    assert tmp_dir2.exists() is False


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "triggers_rerun_-3": 100,
                    },
                    "unode_parameters": {
                        "remove_temporary_files": False,
                    },
                },
            ),
            ["TestNode1:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_unode_delete_tmp_file_pior_run(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    test_node1 = test_nodes["TestNode1:1.0.0"]

    tmp_file = urgap._test_folder / "data" / "tmp.file"
    with open(tmp_file, "w") as fin:
        fin.write("This is gonna be deleted")
    assert tmp_file.exists() is True
    test_node1.tmp_files.append(tmp_file)

    test_node1.run(ufiles=ufiles, urun_dict=urun_dict)

    assert test_node1.tmp_files == []
    tmp_file.unlink()
