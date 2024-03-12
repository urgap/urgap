import logging
from pyvis.network import Network



    graph = nx.DiGraph()

    for (
        unode_name,
        unode_class,
        graph.add_node(unode_name, color="red", size=7)
            graph.add_node(sft, color="blue", size=12)
            graph.add_edge(
                sft,
                unode_name,
                weight=4.7,
                arrow=True,
                color="black",
            )
            leafs = []
            if len(leafs) > 1:
                for the_any_child in leafs:
                    graph.add_edge(
                        the_any_child,
                        sft,
                        weight=4.7,
                        arrow=True,
                        color="black",
                    )
            graph.add_node(oft, color="blue", size=12)
            graph.add_edge(
                unode_name,
                oft,
                weight=4.7,
                arrow=True,
                color="black",
            )

    net = Network(
        height="750px",
        width="100%",
        directed=True,
    )
    net.from_nx(graph)
    net.show_buttons(filter_=["layout", "physics"])
    net.show("all_possible_pipelines.html")


if __name__ == "__main__":
    main()