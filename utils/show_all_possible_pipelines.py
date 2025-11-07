"""Possible Pipeline Visualizer."""

import contextlib
import logging

import networkx as nx

from pyvis.network import Network

import urgap

logger = logging.getLogger(__name__)


def main() -> None:
    """Build network with all possible pipelines."""
    graph = nx.DiGraph()

    for (
        unode_name,
        unode_class,
    ) in urgap.instances.unode_manager.wrapper_lookup.items():
        graph.add_node(unode_name, color="red", size=7)
        for sft in unode_class.META_INFO.get("input_uftypes", {}):
            graph.add_node(sft, color="blue", size=12)
            graph.add_edge(
                sft,
                unode_name,
                weight=4.7,
                arrow=True,
                color="black",
            )
            leafs = []
            with contextlib.suppress(KeyError):
                leafs = urgap.instances.utree_querier.get_leafs_from_node(sft)
            if len(leafs) > 1:
                for the_any_child in leafs:
                    graph.add_edge(
                        the_any_child,
                        sft,
                        weight=4.7,
                        arrow=True,
                        color="black",
                    )
            msg = f"Added {sft} to {unode_name}"
            logger.debug(msg)
        for oft in unode_class.META_INFO.get("output_uftypes", {}):
            graph.add_node(oft, color="blue", size=12)
            graph.add_edge(
                unode_name,
                oft,
                weight=4.7,
                arrow=True,
                color="black",
            )
            msg = f"Added {oft} to {unode_name}"
            logger.debug(msg)

    net = Network(
        height="750px",
        width="100%",
        directed=True,
    )
    net.from_nx(graph)
    net.show_buttons(filter_=["layout", "physics"])
    net.show("all_possible_pipelines.html")
    logger.info("Wrote all_possible_pipelines.html")


if __name__ == "__main__":
    main()
