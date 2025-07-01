from pathlib import Path

import pytest

import urgap


def test_azure_datalake_native_io():
    try:
        urgap.instances.ucredential_manager.get_user("az-dl://code-orange.gsk.com")
    except KeyError:
        pytest.skip("Azure backend not available")
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")

    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}?temp=hot#{content}")
    uf.rebase(
        uri="az-dl://code-orange.gsk.com/clds/data/raw/dvmt/source/clds/flowcytometry"
        "?tenant-id=63982aff-fb6c-4c22-973b-70e4acfb63e6&client-id=f531f934-437c-4a5a-aac2-cd4099125380&temp=hot",
        upload=True,
    )

    object_name = uf.object_name
    uf.purge_local()

    new_uf = urgap.UFile(
        uri=f"az-dl://code-orange.gsk.com/clds/data/raw/dvmt/source/clds/flowcytometry?tenant-id=63982aff-fb6c-4c22-973b-70e4acfb63e6&client-id=f531f934-437c-4a5a-aac2-cd4099125380#{object_name}",
    )

    assert new_uf.remote_object_exists() is True
    assert new_uf.path.read_text() in uf.path.read_text()
    new_uf.purge_local()
    assert new_uf.io.scratch_path.exists() is False
    new_uf.path
    assert new_uf.io.scratch_path.exists() is True
    assert new_uf.tags.get("temp", None) == "hot"