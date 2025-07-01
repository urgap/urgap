from pathlib import Path

import pytest

import urgap


def test_folder_has_uparam_signature():
    folder_with_md5 = Path("./prefix_9e124250617146fdf18f38070f6d4440/")
    assert urgap.ucore.folder_has_uparam_signature(folder_with_md5) is True
    assert urgap.ucore.folder_has_uparam_signature(folder_with_md5) is True

    nonsense = Path("./prefix_random_32372936127fasdf3/")
    assert urgap.ucore.folder_has_uparam_signature(nonsense) is False
    assert urgap.ucore.folder_has_uparam_signature(nonsense) is False


def test_folder_has_uparam_signature_not_md5(change_hash_algorithm):
    _ = change_hash_algorithm
    folder_with_argon2 = Path("./prefix_874b8bb7d98ec8b277c51c711902da5c/")
    with pytest.raises(NotImplementedError):
        assert urgap.ucore.folder_has_uparam_signature(folder_with_argon2) is False


def test_clean_up_scratch_space(tmp_dir):
    assert urgap.scratch_disk.exists()
    urgap.ucore.clean_up_scratch_space()
    assert urgap.scratch_disk.exists() is False


def test_append_query_to_uri():
    uri = "file:///some/test/uri#without/query.file"
    query = "hash=9243749103984&uftype=some_csv&othertag=lookatme"
    new_uri = urgap.ucore.append_query_to_uri(uri, query)
    assert (
        new_uri
        == "file:///some/test/uri?hash=9243749103984&uftype=some_csv&othertag=lookatme#without/query.file"
    )

    uri = "file:///some/test/uri?hash=9243749103984#without/query.file"
    query = "uftype=some_csv&othertag=lookatme"
    new_uri = urgap.ucore.append_query_to_uri(uri, query)
    assert (
        new_uri
        == "file:///some/test/uri?hash=9243749103984&uftype=some_csv&othertag=lookatme#without/query.file"
    )