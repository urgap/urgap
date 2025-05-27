import pytest



def test_node_fail_produces_none():
        [
                f"test_node_data/test.txt",
    )
    result_8 = test_node8.run(
    )
    assert None in result_8
    storage_base_uri = ufiles[0].storage_base_uri
    assert crashed_trace.crashed is True


def test_node_fail_can_be_allowed():
        [
                f"test_node_data/test.txt",
    )
    with pytest.raises(RuntimeError):
        test_node8.run(
        )