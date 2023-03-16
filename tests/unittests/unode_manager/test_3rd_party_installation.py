

def test__test_command():
    is_available = um._test_command(command_list=["ls", "-l"])
    assert is_available is True


def test__test_command_not_available():
    is_available = um._test_command(command_list=["ls", "", "-"])
    # having space in the list will always crash....
    assert is_available is False