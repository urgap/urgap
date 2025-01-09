import pytest



@pytest.mark.parametrize(
)
def test_new_arch_hierarchy(node_name):
    # TODO: Add new Unode tests
    if node.META_INFO["unode_version"] is None:
        for platform, arcs in node.META_INFO["engine"].items():
            if platform == "platform_independent":
                assert "arc_independent" in arcs
            else:
                assert "arm64" or "x86_64" in arcs
                assert "64bit" not in arcs


@pytest.mark.parametrize(
)
def test_new_arc_info(node_name):
    # TODO: Add new Unode tests
    if node.META_INFO["unode_version"] is None:
        for platform, arcs in node.META_INFO["engine"].items():
            if platform == "system":
                assert isinstance(node.META_INFO["engine"]["system"], str)
            elif platform == "platform_independent":
                assert node.resource_subfolder == f"{platform}/arc_independent"
            else:
                for arc, info in arcs.items():
                    if "urn" in info:
                        assert info["urn"].startswith(f"{platform}/{arc}")