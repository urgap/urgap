from pathlib import Path

import urgap


def test_remote_folder_is_set_properly_on_scratch_disk():
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")
    set_path = uf.uuri.get_file_remote_path()
    theoretical_path = base_folder / content
    assert set_path == theoretical_path
