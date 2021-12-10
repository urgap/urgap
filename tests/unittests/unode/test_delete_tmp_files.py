

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