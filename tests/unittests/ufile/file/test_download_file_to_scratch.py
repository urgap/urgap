from pathlib import Path


def test_accessing_path_downloads_file(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    uf.path


def test_purging_removes_local_files(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    uf.path
    uf.purge_local()