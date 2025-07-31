from pathlib import Path

import pytest

import urgap


def test_init_with_wrong_items_raises_typeError(tmp_scratch_disk):
    with pytest.raises(TypeError):
        urgap.UFileList([12, 33])


def test_init_with_right_items(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    assert len(ufl) == 1


def test_setting_wrong_item_raises_typeError(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    with pytest.raises(TypeError):
        ufl[0] = 12


def test_setting_right_item(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    uf2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_2.txt",
    )
    ufl[0] = uf2
    assert ufl[0].object_name == "test_2.txt"


def test_inserting_wrong_item_raises_typeError(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    with pytest.raises(TypeError):
        ufl.insert(0, 12)


def test_inserting_right_item(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    uf2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_2.txt",
    )
    ufl.insert(0, uf2)
    assert ufl[0].object_name == "test_2.txt"


def test_adding_another_with_wrong_type_raises_typeError(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    with pytest.raises(TypeError):
        ufl += [12]


def test_adding_another_ufilelist_perserves_order(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    uf2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_2.txt",
    )
    ufl += [uf, uf2]
    print(ufl)
    assert len(ufl) == 3
    assert ufl[2].object_name == "test_2.txt"


def test_appending_wrong_item_raises_typeError(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    with pytest.raises(TypeError):
        ufl.append(12)


def test_appending_right_item(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    uf2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_2.txt",
    )
    ufl.append(uf2)
    assert ufl[1].object_name == "test_2.txt"


def test_appending_right_nested_item(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])
    uf2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_2.txt",
    )
    ufl.append([uf2])
    assert ufl[1][0].object_name == "test_2.txt"


def test_removing_single_uftypes():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    ufl = ufl.remove_uftypes([urgap.uftypes.test.MITSURUGI])
    assert len(ufl) == 1
    assert urgap.uftypes.test.MITSURUGI not in ufl.get_index_groups_by_uftypes().keys()


def test_remove_single_uftypes_typeerror():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    with pytest.raises(TypeError):
        ufl.remove_uftypes(urgap.uftypes.test.MITSURUGI)


def test_remove_multiple_uftypes():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE2}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]
    ufl = urgap.ufile_list.UFileList(ufiles)

    uftype_list = [urgap.uftypes.test.MITSURUGI, urgap.uftypes.test.TEST_FILE1]
    ufl = ufl.remove_uftypes(uftype_list)
    assert len(ufl) == 1
    for uftype in uftype_list:
        assert uftype not in ufl.get_index_groups_by_uftypes().keys()


def test_keep_single_uftypes():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    ufl = ufl.keep_uftypes([urgap.uftypes.test.MITSURUGI])
    assert len(ufl) == 2
    assert urgap.uftypes.test.MITSURUGI in ufl.get_index_groups_by_uftypes().keys()
    assert urgap.uftypes.test.TEST_FILE1 not in ufl.get_index_groups_by_uftypes().keys()
    assert urgap.uftypes.test.TEST_FILE2 not in ufl.get_index_groups_by_uftypes().keys()


def test_keep_single_uftypes_typeerror():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    with pytest.raises(TypeError):
        ufl.keep_uftypes(urgap.uftypes.test.MITSURUGI)


def test_keep_multiple_uftypes():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE2}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]
    ufl = urgap.ufile_list.UFileList(ufiles)

    uftype_list = [urgap.uftypes.test.MITSURUGI, urgap.uftypes.test.TEST_FILE1]
    ufl = ufl.keep_uftypes(uftype_list)
    assert len(ufl) == 2
    for uftype in uftype_list:
        assert uftype in ufl.get_index_groups_by_uftypes().keys()
    assert urgap.uftypes.test.TEST_FILE2 not in ufl.get_index_groups_by_uftypes().keys()


def test_set_uftype_if_none_available():
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = urgap.UFileList.from_uri_list(
        [f"file://{base_folder}?uftype={urgap.uftypes.unknown.UNKNOWN}#test_1.txt"]
    )
    assert ufiles[0].uftype == urgap.uftypes.any.TXT

    ufiles = urgap.UFileList.from_uri_list(
        [
            f"file://{base_folder}?uftype={urgap.uftypes.unknown.UNKNOWN}#unified_csvs/demo.csv"
        ]
    )
    assert ufiles[0].uftype == urgap.uftypes.any.CSV