import urgap


def test_is_tar():
    compression_format = urgap.util.sense_compression_format(
        urgap._test_folder / "data/compressions/test.tar",
    )
    assert compression_format == "tar"


def test_is_split_tar():
    compression_format = urgap.util.sense_compression_format(
        urgap._test_folder / "data/compressions/split_tars/test_part_aa",
    )
    assert compression_format == "split_tar"

    compression_format = urgap.util.sense_compression_format(
        urgap._test_folder / "data/compressions/split_tars/test_part_ab",
    )
    assert compression_format == "split_tar"


def test_is_zip():
    compression_format = urgap.util.sense_compression_format(
        urgap._test_folder / "data/compressions/asdf.zip",
    )
    assert compression_format == "zip"


def test_is_gz():
    compression_format = urgap.util.sense_compression_format(
        urgap._test_folder / "data/compressions/test.txt.tar.gz",
    )
    assert compression_format == "gz"
