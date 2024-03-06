

def test_same_file_same_location(tmp_file):
        file.write(content)

    assert ufile1 == ufile2


def test_same_file_different_location(tmp_file):
    for path in [tmp_file, second_file]:
            file.write(content)

    assert ufile1 != ufile2