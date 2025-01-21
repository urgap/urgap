from pathlib import Path

import pytest



def test_setting_tags(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")

    uf.tags.update(
    assert uf.tags.get("lo", None) == "12"


def test_updating_tags(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")

    uf.tags.update(
    assert uf.tags.get("lo", None) == "12"
    uf.tags.update({"asdf": "123"})
    assert uf.tags.get("lo", None) == "12"
    assert uf.tags.get("asdf", None) == "123"


@pytest.mark.parametrize(
    "provide_clean_scratch_and_remote",
    [
        ),
    ],
    indirect=["provide_clean_scratch_and_remote"],
)
def test_tags_are_set_via_uri(provide_clean_scratch_and_remote):
    ufile = provide_clean_scratch_and_remote
    uftype_tag = ufile.tags.get("uftype", None)
    qc_tag = ufile.tags.get("qc", None)
    ufile.purge_local()
    assert qc_tag == "good"


@pytest.mark.parametrize(
    "provide_clean_scratch_and_remote",
    [
    ],
    indirect=["provide_clean_scratch_and_remote"],
)
    ufile = provide_clean_scratch_and_remote
    ufile_uri_without_query = ufile.as_uri(query="")
    print("uri without query", ufile_uri_without_query)
    print(ufile.path)

    ufile.tags.update({"qc": "bad"})
    print("After update", ufile.as_uri())
    with open(ufile.path, "w") as o:
        print("Soon gone", file=o)
    ufile.upload()
    ufile.purge_local()
    del ufile
    qc_tag = ufile_2.tags.get("qc", None)
    ufile_2.remove_remote_object()
    assert qc_tag == "bad"


def test_setting_tags_merges_with_remote(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    uf.rebase(f"file://{tmp_scratch_disk}")
    new_uri = uf.as_uri()
    assert "md5" not in new_uri
    assert "md5" in uf.as_uri()
    uf.tags.update({"lo": "12"})
    uf.upload()
    uf.purge_local()
    )
    assert uf2.tags.get("lo", None) == "12"
    assert uf2.tags.get("k", None) == 12
    assert uf2.tags.get("rings", None) == ["one", "to", "rule", "them", "all"]