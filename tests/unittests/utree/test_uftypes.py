import regex as re

import urgap


def test_node_names_are_unique():
    nodes = list(urgap.instances.utree_querier.G.nodes)
    assert len(nodes) == len(set(nodes))


def test_leaf_suffix_nomenclature():
    leafs = set(
        ext for _, ext in urgap.instances.utree_querier.get_leafs_from_node(node="ANY")
    )
    test_leafs = set(
        ext
        for _, ext in urgap.instances.utree_querier.get_leafs_from_node(
            node="test.ANY",
        )
    )
    leafs = leafs.difference(test_leafs).difference({".unknown"})

    suffix_pattern = re.compile(r"^\.[\w]+\.[\w]+$")
    assert all(bool(re.match(suffix_pattern, s)) for s in leafs)