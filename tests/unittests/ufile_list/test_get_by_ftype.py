from pathlib import Path

import urgap


def test_modifying_file_doesnt_change_ufile_list():
    tmp_string = "#unique"
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#{tmp_string}/test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#{tmp_string}/test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#{tmp_string}/test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    # ----
    idx = ufl.get_indices_by_uftype(urgap.uftypes.test.TEST_FILE1)
    # ----

    assert idx == [0]
    assert id(ufl[idx[0]]) == id(ufiles[0])

    with open(ufl[idx[0]].path, "w") as oo:
        print("Jo", file=oo)

    # ----
    idx2 = ufl.get_indices_by_uftype(urgap.uftypes.test.TEST_FILE1)
    # ----

    assert idx2 == [0]
    assert id(ufl[idx2[0]]) == id(ufiles[0])


def test_get_index_groups():
    tmp_string = "#unique"
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#{tmp_string}/test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#{tmp_string}/test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#{tmp_string}/test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    idx_dict = ufl.get_index_groups_by_uftypes()
    assert idx_dict == {
        urgap.uftypes.test.TEST_FILE1: [0],
        urgap.uftypes.test.MITSURUGI: [1, 2],
    }
