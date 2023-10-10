import pytest


def test_azure_native_io(tmp_file):
    with open(tmp_file, "w") as f:
        print("Tea, Earl Grey, hot.", file=f)
    object_name = uf.object_name
    uf.purge_local()

    assert "Earl Grey" in new_uf.path.read_text()