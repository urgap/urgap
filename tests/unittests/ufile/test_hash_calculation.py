from pathlib import Path



def test_md5(tmp_scratch_disk):
    content = Path("test_node_data/test.txt")
    assert uf.hash == "d76ff661869c283077c8d9e4e531e3d9"