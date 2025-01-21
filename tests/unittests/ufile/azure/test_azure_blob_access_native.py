import pytest


def test_azure_native_io(tmp_file):
    try:
    except KeyError:
        pytest.skip("Azure backend not available")
    with open(tmp_file, "w") as f:
        print("Tea, Earl Grey, hot.", file=f)
    object_name = uf.object_name
    uf.purge_local()

    assert "Earl Grey" in new_uf.path.read_text()
    assert new_uf.tags.get("temp", None) == "hot"