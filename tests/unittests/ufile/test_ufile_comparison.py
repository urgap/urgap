import tempfile

from pathlib import Path



def test_same_file_same_location(tmp_file):
    content = "Why so serious?"
    with open(tmp_file, "w") as file:
        file.write(content)

    assert ufile1 == ufile2


def test_same_file_different_location(tmp_file):
    content = "Why so serious?"
    with tempfile.NamedTemporaryFile() as tmp_file_2:
        second_file = Path(tmp_file_2.name)
    for path in [tmp_file, second_file]:
        with open(path, "w") as file:
            file.write(content)

    assert ufile1 != ufile2