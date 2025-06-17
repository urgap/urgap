import os

from pathlib import Path



def test_path_object_to_uri():
    content = Path("test_node_data/test.txt")


def test_path_object_to_uri_multiple_parent_folders():
    ufile_path = Path("this/is/a/path/to/a/ufile")
    assert uri.startswith("file://")
    assert uri.endswith("this/is/a/path/to#a/ufile")
        path_object=ufile_path,
        number_of_parents=0,
    ).as_uri()
    assert uri.endswith("this/is/a/path/to/a#ufile")
        path_object=ufile_path,
        number_of_parents=2,
    ).as_uri()
    assert uri.endswith("this/is/a/path#to/a/ufile")
        path_object=ufile_path,
        number_of_parents=3,
    ).as_uri()
    assert uri.endswith("this/is/a#path/to/a/ufile")


def test_path_object_to_uri_way_too_many_parents():
    content = Path("test_node_data/test.txt")
        path_object=(base_folder / content),
        number_of_parents=200,
    ).as_uri()
    content = os.path.join(base_folder, content)[1:]