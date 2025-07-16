from pathlib import Path

import pytest

import urgap


def test_uuri_scheme_not_supported():
    with pytest.raises(ValueError, match=r"Scheme notsupported not supported"):
        urgap.UFile(
            uri=f"notsupported://{urgap._test_folder}/data#test_node_data/test.txt",
        )


def test_uuri_properties_file_schema():
    uf = urgap.UFile(
        uri=f"file://{urgap._test_folder}/data#test_node_data/test.txt",
    )
    assert uf.uuri.mylabdata_api_url is None
    assert uf.uuri.mylabdata_api_url_files is None
    assert uf.uuri.samba_share is None
    assert uf.uuri.azure_share is None
    assert uf.uuri.azure_directory_list is None
    assert uf.uuri.azure_object_file is None
    assert uf.uuri.azure_object_directory_list is None
    assert uf.uuri.https_remote_path is None
    assert uf.uuri.https_remote_tag_path is None
    assert uf.uuri.host is None
    assert uf.uuri.port is None
    assert uf.uuri.github_resource_name is None
    assert uf.uuri.user is None
    assert uf.uuri.password is None
    assert uf.uuri.file_remote_path == Path(
    )
    assert uf.uuri.file_remote_tag_path == Path(
    )
    assert uf.uuri.container_name == "data"
    assert uf.uuri.object_name == "test_node_data/test.txt"


def test_uuri_properties_mld():