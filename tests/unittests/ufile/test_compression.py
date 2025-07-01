from pathlib import Path

import urgap


def test_uncompress_zip(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("compressions/test.txt.zip")
    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?test_tag=something#{content}",
    )
    new_ufl = uf.uncompress()
    assert new_ufl[0].path.read_text() == "twas_uncompressed"
    assert new_ufl[0].object_name == "test.txt"


def test_uncompress_tar_gz(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("compressions/test.txt.tar.gz")
    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?test_tag=something#{content}",
    )
    new_ufl = uf.uncompress()
    assert new_ufl[0].path.read_text() == "twas_uncompressed"


def test_compress_zip(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("compressions/test.txt")
    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?test_tag=something#{content}",
    )
    new_uf = uf.compress(compression_format="zip")
    assert new_uf.path.exists() is True
    assert new_uf.uncompress()[0].path.read_text() == "twas_uncompressed"
    assert uf.as_uri() + ".zip" == new_uf.as_uri()


def test_compress_tar_gz(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("compressions/test.txt")
    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?test_tag=something#{content}",
    )
    new_uf = uf.compress(compression_format="tar")
    new_uf = new_uf.compress(compression_format="gz")
    assert new_uf.path.exists() is True
    assert new_uf.uncompress()[0].path.read_text() == "twas_uncompressed"
    assert uf.as_uri() + ".tar.gz" == new_uf.as_uri()


def test_multiple_files(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("compressions/asdf.zip")
    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?test_tag=something#{content}",
    )
    new_ufl = uf.uncompress()
    # Directory and two test files
    assert len(new_ufl) == 2
    assert new_ufl[0].path.read_text() == f"test_{new_ufl[0].simple_name}"
    assert new_ufl[1].path.read_text() == f"test_{new_ufl[1].simple_name}"


def test_uncompress_split_tar(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data/compressions/split_tars")
    content = Path("test_part_aa")
    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?test_tag=something#{content}",
    )
    new_ufl = uf.uncompress()
    assert len(new_ufl) == 2
    assert new_ufl[0].object_name == "test.txt"
    assert new_ufl[1].object_name == "test2.txt"