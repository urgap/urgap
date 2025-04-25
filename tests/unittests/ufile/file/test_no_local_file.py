from pathlib import Path

import pytest



def test_accessing_path_downloads_file(tmp_scratch_disk):
    content = Path("test_node_data/doesnt_exist.txt")
    with pytest.raises(FileNotFoundError):
        uf.recalculate_hashes(force_local=True)