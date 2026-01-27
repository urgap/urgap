from pathlib import Path

import urgap


def test_accessing_path_downloads_file(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")
    uf.upload(overwrite=False, verify=True, purge=False)
    assert uf.io.scratch_path.exists() is True
