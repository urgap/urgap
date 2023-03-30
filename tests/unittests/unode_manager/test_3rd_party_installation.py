

def test__test_command():
    is_available = um._test_command(command_list=["ls", "-l"])
    assert is_available is True


def test__test_command_not_available():
    is_available = um._test_command(command_list=["ls", "", "-"])
    # having space in the list will always crash....
    assert is_available is False


def test_has_all_required_third_party_installs_without_init():
    assert test_node.has_all_required_installations() is True
    assert test_node.has_all_required_installations() is True