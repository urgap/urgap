from pathlib import Path



def test_uncompress_split_tar(tmp_scratch_disk):
    ufl.uncompress(destination=tmp_scratch_disk / "test")
    assert len(new_ufl) == 2
    assert new_ufl[0].object_name == "test.txt"
    assert new_ufl[1].object_name == "test2.txt"