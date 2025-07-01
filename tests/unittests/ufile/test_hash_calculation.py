from pathlib import Path

import urgap


def test_md5(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")
    uf = urgap.UFile(uri=f"file://{base_folder.resolve()}#{content}")
    assert uf.hash == "d76ff661869c283077c8d9e4e531e3d9"