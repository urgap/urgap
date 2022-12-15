from pathlib import Path

import pytest



def test_init_with_wrong_items_raises_typeError(tmp_scratch_disk):
    with pytest.raises(TypeError):


def test_init_with_right_items(tmp_scratch_disk):

    )
    assert len(ufl) == 1


def test_setting_wrong_item_raises_typeError(tmp_scratch_disk):

    )
    with pytest.raises(TypeError):
        ufl[0] = 12


def test_setting_right_item(tmp_scratch_disk):

    )
    )
    ufl[0] = uf2
    assert ufl[0].object_name == "test_2.txt"


def test_inserting_wrong_item_raises_typeError(tmp_scratch_disk):

    )
    with pytest.raises(TypeError):
        ufl.insert(0, 12)


def test_inserting_right_item(tmp_scratch_disk):

    )
    )
    ufl.insert(0, uf2)
    assert ufl[0].object_name == "test_2.txt"


def test_adding_another_with_wrong_type_raises_typeError(tmp_scratch_disk):

    )
    with pytest.raises(TypeError):
        ufl += [12]


def test_adding_another_ufilelist_perserves_order(tmp_scratch_disk):

    )
    )
    ufl += [uf, uf2]
    print(ufl)
    assert len(ufl) == 3
    assert ufl[2].object_name == "test_2.txt"


def test_appending_wrong_item_raises_typeError(tmp_scratch_disk):

    )
    with pytest.raises(TypeError):
        ufl.append(12)


def test_appending_right_item(tmp_scratch_disk):

    )
    )
    ufl.append(uf2)
    assert ufl[1].object_name == "test_2.txt"


def test_appending_right_nested_item(tmp_scratch_disk):

    )
    )
    ufl.append([uf2])
    assert ufl[1][0].object_name == "test_2.txt"


def test_removing_single_uftypes():
    ufiles = [
        ),
        ),
        ),
    ]

    assert len(ufl) == 1


def test_remove_single_uftypes_typeerror():
    ufiles = [
        ),
        ),
        ),
    ]

    with pytest.raises(TypeError):


def test_remove_multiple_uftypes():
    ufiles = [
        ),
        ),
        ),
    ]

    ufl = ufl.remove_uftypes(uftype_list)
    assert len(ufl) == 1
    for uftype in uftype_list:
        assert uftype not in ufl.get_index_groups_by_uftypes().keys()


def test_keep_single_uftypes():
    ufiles = [
        ),
        ),
        ),
    ]

    assert len(ufl) == 2


def test_keep_single_uftypes_typeerror():
    ufiles = [
        ),
        ),
        ),
    ]

    with pytest.raises(TypeError):


def test_keep_multiple_uftypes():
    ufiles = [
        ),
        ),
        ),
    ]

    ufl = ufl.keep_uftypes(uftype_list)
    assert len(ufl) == 2
    for uftype in uftype_list:
        assert uftype in ufl.get_index_groups_by_uftypes().keys()