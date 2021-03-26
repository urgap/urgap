


        fin.write("This is gonna be deleted")
    assert tmp_file.exists() is True
    test_node1.tmp_files.append(tmp_file)

    tmp_file.unlink()