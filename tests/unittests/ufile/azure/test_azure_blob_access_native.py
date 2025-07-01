import pytest

import urgap


def test_azure_native_io(tmp_file):
    try:
        urgap.instances.ucredential_manager.get_user("azure://a-launch-i.gsk.com")
    except KeyError:
        pytest.skip("Azure backend not available")
    with open(tmp_file, "w") as f:
        print("Tea, Earl Grey, hot.", file=f)
    uf = urgap.UFile.from_path_object(path_object=tmp_file, query="temp=hot")
    uf.rebase(uri="azure://a-launch-i.gsk.com/test-urgap", upload=True)
    object_name = uf.object_name
    uf.purge_local()

    new_uf = urgap.UFile(uri=f"azure://a-launch-i.gsk.com/test-urgap#{object_name}")
    assert "Earl Grey" in new_uf.path.read_text()
    assert new_uf.tags.get("temp", None) == "hot"