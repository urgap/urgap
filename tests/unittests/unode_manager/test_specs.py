

def test_simple_python():
    assert is_available is True


def test_simple_python_with_missing():
    is_available = um.check_requirements(
    )
    assert is_available is False


def test_external_resource_test_dict_points_to_unavailable_for_req3():
        external_resource_test_dict={
            "super_req3": {
                "command": ["ls", "", "-"],
                # space in command_list will crash
            },
        },
    )
    is_available = um.check_requirements(
        requirements={"other_dependencies": ["super_req3"]},
    )
    assert um.availability["other_dependencies"]["super_req3"] is False
    assert is_available is False


def test_cobo_python_and_external():
        external_resource_test_dict={
            "super_req3": {
                "command": ["ls", "", "-"],
                # space in command_list will crash
            },
        },
    )
    is_available = um.check_requirements(
        requirements={
            "other_dependencies": ["super_req3"],
        },
    )
    assert is_available is False