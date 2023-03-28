import regex as re



def test_node_names_are_unique():
    assert len(nodes) == len(set(nodes))


def test_leaf_suffix_nomenclature():
    leafs = set(
    )
    test_leafs = set(
        ext
        )
    )
    leafs = leafs.difference(test_leafs).difference({".unknown"})

    suffix_pattern = re.compile(r"^\.[\w]+\.[\w]+$")
    assert all(bool(re.match(suffix_pattern, s)) for s in leafs)