import pytest



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


def test__check_for_module():
    no_version = um._check_for_module("definitely_no_module")
    assert no_version is None
    pandas_version = um._check_for_module("pandas")
    assert pandas_version is not None


@pytest.mark.parametrize(
    "requirements",
    [
        ({"python_packages": ["pandas"]}, True),
        ({"python_packages": ["no_package_for_sure"]}, False),
    ],
)
def test_check_pypackage_requirements(requirements):
    reqs, expected = requirements
    is_available = um.check_requirements(requirements=reqs)
    assert is_available is expected