import tempfile

from pathlib import Path

import urgap


def test_same_file_same_location(tmp_file):
    content = "Why so serious?"
    with open(tmp_file, "w") as file:
        file.write(content)
    base = tmp_file.parent
    filename = tmp_file.name
    ufile1 = urgap.UFile(uri=f"file://{base}#{filename}")
    ufile2 = urgap.UFile(uri=f"file://{base}#{filename}")

    assert ufile1 == ufile2


def test_same_file_different_location(tmp_file):
    content = "Why so serious?"
    with tempfile.NamedTemporaryFile() as tmp_file_2:
        second_file = Path(tmp_file_2.name)
    for path in [tmp_file, second_file]:
        with open(path, "w") as file:
            file.write(content)
    ufile1 = urgap.UFile.from_path_object(path_object=tmp_file)
    ufile2 = urgap.UFile.from_path_object(path_object=second_file)

    assert ufile1.hash == ufile2.hash
    assert ufile1 != ufile2
