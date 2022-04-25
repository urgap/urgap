from pathlib import Path


def test_uncompress_zip(tmp_scratch_disk):
    content = Path("compressions/test.txt.zip")
    )


def test_uncompress_tar_gz(tmp_scratch_disk):
    content = Path("compressions/test.txt.tar.gz")
    )


def test_compress_zip(tmp_scratch_disk):
    content = Path("compressions/test.txt")
    )
    assert new_uf.path.exists() is True
    assert uf.as_uri() + ".zip" == new_uf.as_uri()


def test_compress_tar_gz(tmp_scratch_disk):
    content = Path("compressions/test.txt")
    )
    assert new_uf.path.exists() is True
    assert uf.as_uri() + ".tar.gz" == new_uf.as_uri()