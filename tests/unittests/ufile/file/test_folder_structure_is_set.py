from pathlib import Path


def test_folder_is_set_properly_on_scratch_disk():
    content = Path("test_node_data/test.txt")
    set_path = uf.io.scratch_path