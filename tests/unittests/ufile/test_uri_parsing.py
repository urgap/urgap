import pytest

import urgap


def test_parsing_uri_or_ucfs_and_storage_base_is_the_same():
    ufile_1 = urgap.UFile(
        uri=f"file://{urgap._test_folder}/data#test_node_data/test.txt",
    )
    ufile_2 = urgap.UFile(
        uri=f"file://{urgap._test_folder}/data#test_node_data/test.txt",
    )
    assert ufile_1.as_uri() == ufile_2.as_uri()