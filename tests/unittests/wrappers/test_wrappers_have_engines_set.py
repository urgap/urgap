import pytest

import urgap


@pytest.mark.parametrize(
    "node_name",
    urgap.instances.unode_manager.wrapper_lookup.keys(),
)
def test_all_engines_present(node_name):
    node = urgap.init_node(node_name)
    if node.META_INFO["unode_version"] is None:
        if node.META_INFO["platform_independent"]:
            assert any(
                [
                    engine in node.META_INFO["engine"]
                    for engine in ("platform_independent", "system")
                ],
            )
        else:
            assert any(
                [
                    engine in node.META_INFO["engine"]
                    for engine in ("darwin", "linux", "win32", "system")
                ],
            )