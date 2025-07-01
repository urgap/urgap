import urgap


def test_wrapper_lookup_with_old_wrappers():
    wrapper_lookup = urgap.instances.unode_manager.wrapper_lookup
    assert all(
        key in wrapper_lookup.keys()
        for key in [
            "BasicFunctionTestNode:0.0.5",
            "BasicFunctionTestNode:latest",
            "BasicFunctionTestNode:1.1.0",
        ]
    )
    unode = urgap.init_unode("BasicFunctionTestNode:1.1.0")
    assert str(unode.exe_path).endswith(
        ".urgap/resources/TestNodes/BasicFunctionTestNode/1_1_0/basic_function.py",
    )
    unode = urgap.init_unode("BasicFunctionTestNode:0.0.5")
    assert (
        unode.META_INFO["versions"][0]["exe_path"]
        == "BasicFunctionTestNode/0_0_5/basic_function.py"
    )
    unode = urgap.init_unode("BasicFunctionTestNode:latest")
    assert len(unode.META_INFO["versions"]) >= 2