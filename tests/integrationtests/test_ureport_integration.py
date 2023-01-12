import networkx



    )

    assert isinstance(ur.graph, networkx.classes.digraph.DiGraph) is True

    filtered_1 = filter_node.run(
        ufiles=[input_file],
    )
    filtered_1b = filter_node.run(
        ufiles=[input_file],
    )
    filtered_1c = filter_node.run(
        ufiles=filtered_1b,
    )
    filtered_2 = filter_node.run(
        ufiles=[filtered_1, filtered_1c, input_file],
    )

    assert len(ur.graph.nodes) == 9