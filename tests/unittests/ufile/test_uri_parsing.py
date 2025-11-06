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


def test_uuri_is_set_properly_by_uri():
    ufile_1 = urgap.UFile(
        uri=f"azure://{urgap._test_folder}/data#bridge/console4.io",
    )
    assert ufile_1.uuri.scheme == "azure"
    assert ufile_1.uuri.get_container_name() == "data"
    assert ufile_1.object_name == "bridge/console4.io"


def test_uuri_is_set_properly_case_query1():
    ufile_1 = urgap.UFile(
        uri=f"azure://{urgap._test_folder}/data?test=True#bridge/console4.io",
    )
    assert ufile_1.uuri.scheme == "azure"
    assert ufile_1.uuri.get_container_name() == "data"
    assert ufile_1.object_name == "bridge/console4.io"
    assert ufile_1.uuri.query["test"] is True


def test_query_is_in_wrong_position_in_uri():
    with pytest.raises(ValueError):
        urgap.UFile(
            uri=f"azure://{urgap._test_folder}/data#bridge/console4.io?test=True",
        )


def test_as_storage_uri_is_correct_basic():
    ufile_1 = urgap.UFile(
        uri=f"azure://{urgap._test_folder}/data#bridge/console4.io",
    )
    assert ufile_1.as_storage_base_uri() == f"azure://{urgap._test_folder}/data"


def test_as_storage_uri_is_correct_incl_port():
    ufile_1 = urgap.UFile(
        uri="azure://fufezan.net:80/data#bridge/console4.io",
    )
    assert ufile_1.as_storage_base_uri() == "azure://fufezan.net:80/data"