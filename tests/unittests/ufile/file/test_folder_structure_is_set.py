from pathlib import Path

import urgap


def test_folder_is_set_properly_on_scratch_disk():
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")
    set_path = uf.io.scratch_path
    theoretical_path = Path(urgap.scratch_disk / base_folder.name / content)
    for tp in theoretical_path.parts:
        assert tp in set_path.parts
