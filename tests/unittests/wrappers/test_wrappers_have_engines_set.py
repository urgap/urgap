import pytest



@pytest.mark.parametrize(
)
def test_all_engines_present(node_name):
        if node.META_INFO["platform_independent"]:
            assert any(
                [
                    engine in node.META_INFO["engine"]
                    for engine in ("platform_independent", "system")
            )
        else:
            assert any(
                [
                    engine in node.META_INFO["engine"]
                    for engine in ("darwin", "linux", "win32", "system")
            )