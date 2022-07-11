from pathlib import Path



def test_uncompress_zip(tmp_scratch_disk):
    content = Path("compressions/test.txt.zip")
    )


def test_uncompress_tar_gz(tmp_scratch_disk):
    content = Path("compressions/test.txt.tar.gz")
    )
    new_ufl = uf.uncompress()
    assert new_ufl[0].path.read_text() == "twas_uncompressed"


def test_compress_zip(tmp_scratch_disk):
    content = Path("compressions/test.txt")
    )
    assert new_uf.path.exists() is True
    assert uf.as_uri() + ".zip" == new_uf.as_uri()


def test_compress_tar_gz(tmp_scratch_disk):
    content = Path("compressions/test.txt")
    )
    assert new_uf.path.exists() is True
    assert new_uf.uncompress()[0].path.read_text() == "twas_uncompressed"
    assert uf.as_uri() + ".tar.gz" == new_uf.as_uri()