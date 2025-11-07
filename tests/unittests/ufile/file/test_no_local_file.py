from pathlib import Path

import pytest

import urgap


def test_accessing_path_downloads_file(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/doesnt_exist.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")
    with pytest.raises(FileNotFoundError):
        uf.recalculate_hashes(force_local=True)
