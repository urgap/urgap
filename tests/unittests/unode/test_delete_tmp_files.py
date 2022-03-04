import os

import pytest



def test_unode_delete_tmp_file():
        fin.write("This is gonna be deleted")
    assert tmp_file.exists() is True
    test_node.tmp_files.append(str(tmp_file))
    test_node.delete_tmp_files()

    assert tmp_file.exists() is False


def test_unode_delete_tmp_dir():
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
            ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_unode_delete_tmp_file_pior_run(provide_clean_test_node_dirs):

        fin.write("This is gonna be deleted")
    assert tmp_file.exists() is True
    test_node1.tmp_files.append(tmp_file)


    assert test_node1.tmp_files == []
    tmp_file.unlink()