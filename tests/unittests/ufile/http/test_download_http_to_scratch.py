from pathlib import Path


def test_accessing_path_downloads_file(tmp_scratch_disk):
    assert uf.io.scratch_path.exists() is False
    uf.path
    assert uf.io.scratch_path.exists() is True