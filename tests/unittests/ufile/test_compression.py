from pathlib import Path



def test_uncompress_zip(tmp_scratch_disk):
    content = Path("compressions/test.txt.zip")
    )
    new_ufl = uf.uncompress()
    assert new_ufl[0].path.read_text() == "twas_uncompressed"


def test_uncompress_tar_gz(tmp_scratch_disk):
    content = Path("compressions/test.txt.tar.gz")
    )
    new_ufl = uf.uncompress()
    assert new_ufl[0].path.read_text() == "twas_uncompressed"


def test_compress_zip(tmp_scratch_disk):
    content = Path("compressions/test.txt")
    )
    assert new_uf.path.exists() is True
    assert new_uf.uncompress()[0].path.read_text() == "twas_uncompressed"
    assert uf.as_uri() + ".zip" == new_uf.as_uri()


def test_compress_tar_gz(tmp_scratch_disk):
    content = Path("compressions/test.txt")
    )
    assert new_uf.path.exists() is True
    assert new_uf.uncompress()[0].path.read_text() == "twas_uncompressed"
    assert uf.as_uri() + ".tar.gz" == new_uf.as_uri()


def test_multiple_files(tmp_scratch_disk):
    content = Path("compressions/asdf.zip")
    )
    new_ufl = uf.uncompress()
    # Directory and two test files
    assert len(new_ufl) == 2
    assert new_ufl[0].path.read_text() == f"test_{new_ufl[0].simple_name}"
    assert new_ufl[1].path.read_text() == f"test_{new_ufl[1].simple_name}"