from pathlib import Path

import pytest

import urgap


_CORE_KNOWN_SCHEMES = frozenset({
    "azure", "az-dl", "az-smb", "file", "ftp", "gcs",
    "github", "https", "mylabdata", "omiq", "smb",
})

def check_uri_scheme_exists(self) -> None:
    scheme = self.uuri.scheme
    available_schemes = urgap.instances.ufile_io_manager.available_io_classes
    if scheme not in _CORE_KNOWN_SCHEMES and scheme not in available_schemes:
        msg = f"Scheme {scheme} not supported"
        raise ValueError(msg)


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
        f"{urgap._test_folder}/data/test_node_data/test.txt",
    )
    assert uf.uuri.file_remote_tag_path == Path(
        f"{urgap._test_folder}/data/test_node_data/test.txt.tag",
    )
    assert uf.uuri.container_name == "data"
    assert uf.uuri.object_name == "test_node_data/test.txt"


def test_uuri_properties_mld():
    uuri = urgap.UUri(uri="mylabdata://dummy#test")
    assert uuri.mylabdata_api_url == "https://dummy"
    assert uuri.mylabdata_api_url_files == "https://dummy/files"


def test_uuri_properties_samba():
    uf = urgap.UFile(uri="smb://dummy.test/share/folder#test_node_data/test.txt")
    assert uf.uuri.samba_share == "share/folder"
    assert uf.uuri.file_remote_path is None
    assert uf.uuri.file_remote_tag_path is None


def test_uuri_properties_azure_samba():
    uf = urgap.UFile(uri="az-smb://dummy.test/share/folder#test_node_data/test.txt")
    assert uf.uuri.azure_share == "share"
    assert uf.uuri.azure_directory_list == ["folder"]
    assert uf.uuri.azure_object_file == "test.txt"
    assert uf.uuri.azure_object_directory_list == ["test_node_data"]

    uf2 = urgap.UFile(uri="az-smb://dummy.test/share/folder#test.txt")
    assert uf2.uuri.azure_object_directory_list == []


def test_uuri_properties_https():
    ufile = urgap.UFile(
        uri="https://github.com/gsk-tech/pymx/raw/main/example_scripts"
        "#filter_nonbiological_ions_1_0_0.py",
    )
    assert (
        ufile.uuri.https_remote_path
        == "https://github.com/gsk-tech/pymx/raw/main/example_scripts/filter_nonbiological_ions_1_0_0.py"
    )
    assert (
        ufile.uuri.https_remote_tag_path
        == "https://github.com/gsk-tech/pymx/raw/main/example_scripts/filter_nonbiological_ions_1_0_0.py.tag"
    )
