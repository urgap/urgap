

def test_get_all_relevant_nodes():
    to_spawn = get_all_relevant_nodes("BasicFunctionTestNode:latest")
    assert len(to_spawn) == 2
    assert to_spawn == ["BasicFunctionTestNode:latest", "BasicFunctionTestNode:1.3.0"]

    to_spawn = get_all_relevant_nodes("BasicFunctionTestNode:1.3.0")
    assert len(to_spawn) == 2
    assert to_spawn == ["BasicFunctionTestNode:1.3.0", "BasicFunctionTestNode:latest"]

    to_spawn = get_all_relevant_nodes("BasicFunctionTestNode:1.1.0")
    assert len(to_spawn) == 1
    assert to_spawn == ["BasicFunctionTestNode:1.1.0"]