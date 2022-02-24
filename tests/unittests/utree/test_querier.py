

def test_graph_is_built_on_init():


    assert len(querier.get_leafs_from_node(node="test.rumpel.ANY")) == 2
    assert len(querier.get_leafs_from_node(node="test.rumpel.MORE")) == 1


        "test.rumpel.MORE",
        "test.rumpel.ANY",
        "test.ANY",
        "ANY",
    ]
        "test.ANY",
        "ANY",
    ]