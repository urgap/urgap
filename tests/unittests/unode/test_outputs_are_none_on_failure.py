import pytest



def test_node_fail_produces_none():
        [
                f"test_node_data/test.txt",
    )
    )
    assert crashed_trace.crashed is True


def test_node_fail_can_be_allowed():
        [
                f"test_node_data/test.txt",
    )
    with pytest.raises(RuntimeError):
        )