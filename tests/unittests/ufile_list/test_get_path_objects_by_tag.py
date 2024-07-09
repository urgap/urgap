from pathlib import Path



def test_modifying_file_doesnt_change_ufile_list():
    tmp_string = "#unique"
    ufiles = [
        ),
        ),
        ),
    ]

    index_groups = ufl.get_index_groups_by_tag(tag="testtag")

    assert len(index_groups) == 2
    assert index_groups["asdf"] == [0, 1]
    assert index_groups["jkl"] == [2]