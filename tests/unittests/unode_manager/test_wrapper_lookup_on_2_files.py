

def test_wrapper_lookup_with_old_wrappers():
    assert all(
        key in wrapper_lookup.keys()
        for key in [
            "BasicFunctionTestNode:0.0.5",
            "BasicFunctionTestNode:latest",
            "BasicFunctionTestNode:1.1.0",
        ]
    )
    assert (
        unode.META_INFO["versions"][0]["exe_path"]
        == "BasicFunctionTestNode/0_0_5/basic_function.py"
    )