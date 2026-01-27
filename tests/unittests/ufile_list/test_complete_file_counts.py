import urgap


def test_complete_file_counts_single():
    uf = urgap.UFile(
        uri=f"file://{urgap._test_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1_of_N.txt",
    )
    ufl = urgap.UFileList([uf])
    ufl.complete_file_counts()
    assert ufl[0].simple_name == "test_1_of_1"


def test_complete_file_counts_multiple():
    ufl = urgap.UFileList()
    for i in range(1, 4):
        ufl.append(
            urgap.UFile(
                uri=f"file://{urgap._test_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_{i}_of_N.txt",
            ),
        )
    ufl.complete_file_counts()
    assert set(uf.simple_name for uf in ufl) == {
        "test_1_of_3",
        "test_2_of_3",
        "test_3_of_3",
    }


def test_only_correct_are_set():
    ufl = urgap.UFileList()
    for i in range(1, 4):
        ufl.append(
            urgap.UFile(
                uri=f"file://{urgap._test_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_{i}_of_N.txt",
            ),
        )
    ufl.append(
        urgap.UFile(
            uri=f"file://{urgap._test_folder}?uftype={urgap.uftypes.test.TEST_FILE2}#different_1_of_N.txt",
        ),
    )
    ufl.append(
        urgap.UFile(
            uri=f"file://{urgap._test_folder}?uftype={urgap.uftypes.test.MITSURUGI}#bait_1.txt",
        ),
    )
    ufl.complete_file_counts()
    assert set(uf.simple_name for uf in ufl) == {
        "test_1_of_3",
        "test_2_of_3",
        "test_3_of_3",
        "different_1_of_1",
        "bait_1",
    }
