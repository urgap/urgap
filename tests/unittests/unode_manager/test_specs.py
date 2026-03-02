import urgap


def test_simple_python():
    um = urgap.UNodeManager()
    is_available = um.check_requirements(requirements={"python_packages": ["urgap"]})
    assert is_available is True
    assert "urgap" in um.availability["python_packages"].keys()
    assert um.availability["python_packages"]["urgap"] is True


def test_simple_python_with_missing():
    um = urgap.UNodeManager()
    is_available = um.check_requirements(
        requirements={"python_packages": ["urgap", "urgap_31231"]},
    )
    assert is_available is False
    assert um.availability["python_packages"]["urgap"] is True
    assert um.availability["python_packages"]["urgap_31231"] is False


def test_external_resource_test_dict_points_to_unavailable_for_req3():
    um = urgap.UNodeManager(
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
    um = urgap.UNodeManager(
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
            "python_packages": ["urgap"],
        },
    )
    assert is_available is False
