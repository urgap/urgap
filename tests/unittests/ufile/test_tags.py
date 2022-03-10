from pathlib import Path
import pytest


def test_setting_tags(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")



def test_updating_tags(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")



@pytest.mark.parametrize(
    "provide_clean_scratch_and_remote",
    [
        ),
    ],
    indirect=["provide_clean_scratch_and_remote"],
)
def test_tags_are_set_via_uri(provide_clean_scratch_and_remote):
    ufile = provide_clean_scratch_and_remote
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

    print("After update", ufile.as_uri())
    with open(ufile.path, "w") as o:
        print("Soon gone", file=o)
    ufile.upload()
    ufile.purge_local()
    del ufile
    ufile_2.remove_remote_object()
    assert qc_tag == "bad"