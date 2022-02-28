from pathlib import Path


def test_modifying_file_doesnt_change_ufile_list():
    tmp_string = "#unique"
    ufiles = [
        ),
        ),
        ),
    ]

    # ----
    # ----

    assert idx == [0]
    assert id(ufl[idx[0]]) == id(ufiles[0])

    with open(ufl[idx[0]].path, "w") as oo:
        print("Jo", file=oo)

    # ----
    # ----

    assert idx2 == [0]
    assert id(ufl[idx2[0]]) == id(ufiles[0])


def test_get_index_groups():
    tmp_string = "#unique"
    ufiles = [
        ),
        ),
        ),
    ]

    assert idx_dict == {
    }