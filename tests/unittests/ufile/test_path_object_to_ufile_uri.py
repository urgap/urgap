import os

from pathlib import Path
from urllib.parse import urlparse

import urgap


def _without_query(u: str) -> str:
    p = urlparse(u)
    return f"{p.scheme}://{p.netloc}{p.path}#{p.fragment}"


def test_path_object_to_uri():
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uri = urgap.UFile.from_path_object(base_folder / content).as_uri()
    assert _without_query(uri) == f"file://{base_folder.resolve()}#{content}"


def test_path_object_to_uri_multiple_parent_folders():
    ufile_path = Path("this/is/a/path/to/a/ufile")
    uri = urgap.UFile.from_path_object(path_object=ufile_path).as_uri()
    assert uri.startswith("file://")
    assert uri.endswith("this/is/a/path/to#a/ufile")
    uri = urgap.UFile.from_path_object(
        path_object=ufile_path,
        number_of_parents=0,
    ).as_uri()
    assert uri.endswith("this/is/a/path/to/a#ufile")
    uri = urgap.UFile.from_path_object(
        path_object=ufile_path,
        number_of_parents=2,
    ).as_uri()
    assert uri.endswith("this/is/a/path#to/a/ufile")
    uri = urgap.UFile.from_path_object(
        path_object=ufile_path,
        number_of_parents=3,
    ).as_uri()
    assert uri.endswith("this/is/a#path/to/a/ufile")


def test_path_object_to_uri_way_too_many_parents():
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uri = urgap.UFile.from_path_object(
        path_object=(base_folder / content),
        number_of_parents=200,
    ).as_uri()
    content = os.path.join(base_folder, content)[1:]
    assert _without_query(uri) == f"file:///#{content}"
