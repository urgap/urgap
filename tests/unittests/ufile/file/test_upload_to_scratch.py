from pathlib import Path



def test_accessing_path_downloads_file(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    assert uf.io.scratch_path.exists() is True