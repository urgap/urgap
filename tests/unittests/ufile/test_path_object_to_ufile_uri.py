


def test_path_object_to_uri():
    content = Path("test_node_data/test.txt")


def test_path_object_to_uri_multiple_parent_folders():
    ufile_path = Path("this/is/a/path/to/a/ufile")
    assert uri.startswith("file://")
    assert uri.endswith("this/is/a/path/to#a/ufile")
    assert uri.endswith("this/is/a/path/to/a#ufile")
    assert uri.endswith("this/is/a/path#to/a/ufile")
    assert uri.endswith("this/is/a#path/to/a/ufile")