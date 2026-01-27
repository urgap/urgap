import urgap


def test_graph_is_built_on_init():
    assert isinstance(urgap.instances.utree_querier, urgap.utree.UTreeQuerier)
    assert urgap.instances.utree_querier.G.number_of_nodes() > 0


def test_get_leafs():
    querier = urgap.utree.UTreeQuerier()
    assert len(querier.get_leafs_from_node(node="test.ANY")) == 7
    assert len(querier.get_leafs_from_node(node="test.rumpel.ANY")) == 2
    assert len(querier.get_leafs_from_node(node="test.rumpel.MORE")) == 1


def test_to_root():
    querier = urgap.utree.UTreeQuerier()
    assert [node for node, _ in querier.to_root(node=".more")] == [
        "test.rumpel.MORE",
        "test.rumpel.ANY",
        "test.ANY",
        "ANY",
    ]
    assert [node for node, _ in querier.to_root(node=".test_file1")] == [
        "test.TEST_FILE1",
        "test.ANY",
        "ANY",
    ]
