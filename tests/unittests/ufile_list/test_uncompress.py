from pathlib import Path

import urgap


def test_uncompress_split_tar(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    ufl = urgap.UFileList.from_folder(base_folder / "compressions/split_tars")
    ufl.uncompress(destination=tmp_scratch_disk / "test")
    new_ufl = sorted(urgap.UFileList.from_folder(tmp_scratch_disk / "test"))
    assert len(new_ufl) == 2
    assert new_ufl[0].object_name == "test.txt"
    assert new_ufl[1].object_name == "test2.txt"