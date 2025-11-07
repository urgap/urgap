from pathlib import Path

import pytest

import urgap


def test_setting_tags(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")

    uf.tags.update(
        {"lo": "12"},
    )  # drüberbügeln  what function would raise warning ? add_tags?
    assert uf.tags.get("lo", None) == "12"


def test_updating_tags(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")

    uf.tags.update(
        {"lo": "12"},
    )  # drüberbügeln  what function would raise warning ? add_tags?
    assert uf.tags.get("lo", None) == "12"
    uf.tags.update({"asdf": "123"})
    assert uf.tags.get("lo", None) == "12"
    assert uf.tags.get("asdf", None) == "123"


@pytest.mark.parametrize(
    "provide_clean_scratch_and_remote",
    [
        urgap.UFile(
            uri=f"minio-libcloud://localhost:9000/data?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good&minio-libcloud=yea#"
            f"test_node_data/test_MINIO.txt",
        ),
        urgap.UFile(
            uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good&file=yea#"
            f"test_node_data/test_FILE.txt",
        ),
        urgap.UFile(
            uri=f"gcs-libcloud://urgap_test?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good#"
            f"test_node_data/test_GCS.txt",
        ),
        urgap.UFile(
            uri=f"local-libcloud://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good#"
            f"test_node_data/test_LOCAL.txt",
        ),
    ],
    indirect=["provide_clean_scratch_and_remote"],
)
def test_tags_are_set_via_uri(provide_clean_scratch_and_remote):
    ufile = provide_clean_scratch_and_remote
    if ufile.io.driver is None:
        pytest.skip()
    uftype_tag = ufile.tags.get("uftype", None)
    qc_tag = ufile.tags.get("qc", None)
    ufile.purge_local()
    assert uftype_tag == urgap.uftypes.test.TEST_FILE1
    assert qc_tag == "good"


@pytest.mark.parametrize(
    "provide_clean_scratch_and_remote",
    [
        urgap.UFile(
            uri=f"minio-libcloud://localhost:9000/data?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good&minio-libcloud=yea#"
            f"test_node_data/test_MINIO.txt",
        ),
        urgap.UFile(
            uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good&file=yea#"
            f"test_node_data/test_FILE.txt",
        ),
        urgap.UFile(
            uri=f"gcs-libcloud://urgap_test?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good#"
            f"test_node_data/test_GCS.txt",
        ),
        urgap.UFile(
            uri=f"local-libcloud://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}&qc=good#"
            f"test_node_data/test_LOCAL.txt",
        ),
    ],
    indirect=["provide_clean_scratch_and_remote"],
)
def test_tags_are_read_remotely(provide_clean_scratch_and_remote, tmpdir):
    ufile = provide_clean_scratch_and_remote
    ufile.rebase(f"file://{tmpdir}")
    ufile_uri_without_query = ufile.as_uri(query="")
    print(ufile.uuri)
    print("uri without query", ufile_uri_without_query)
    print(ufile.path)

    ufile.tags.update({"qc": "bad"})
    print("After update", ufile.as_uri())
    with open(ufile.path, "w") as o:
        print("Soon gone", file=o)
    ufile.upload()
    # should sync tags
    ufile.purge_local()
    del ufile
    ufile_2 = urgap.UFile(uri=ufile_uri_without_query)
    qc_tag = ufile_2.tags.get("qc", None)
    ufile_2.remove_remote_object()
    assert qc_tag == "bad"


def test_setting_tags_merges_with_remote(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")
    uf.rebase(f"file://{tmp_scratch_disk}")
    new_uri = uf.as_uri()
    assert "md5" not in new_uri
    uf.hash
    assert "md5" in uf.as_uri()
    uf.tags.update({"lo": "12"})
    uf.upload()
    uf.purge_local()
    new_uri_with_queries = urgap.ucore.append_query_to_uri(
        uri=new_uri,
        query='k=12&rings=["one", "to", "rule", "them", "all"]',
    )
    uf2 = urgap.UFile(uri=new_uri_with_queries)
    assert uf2.tags.get("lo", None) == "12"
    assert uf2.tags.get("k", None) == 12
    assert uf2.tags.get("rings", None) == ["one", "to", "rule", "them", "all"]
