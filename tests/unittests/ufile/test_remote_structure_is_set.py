from pathlib import Path



def test_remote_folder_is_set_properly_on_scratch_disk():
    content = Path("test_node_data/test.txt")
    theoretical_path = base_folder / content
    assert set_path == theoretical_path