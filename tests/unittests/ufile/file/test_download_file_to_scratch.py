from pathlib import Path


def test_accessing_path_downloads_file(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    assert uf.io.scratch_path.exists() is False
    uf.path
    assert uf.io.scratch_path.exists() is True


def test_purging_removes_local_files(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    assert uf.io.scratch_path.exists() is False
    uf.path
    assert uf.io.scratch_path.exists() is True
    uf.purge_local()
    assert uf.io.scratch_path.exists() is False