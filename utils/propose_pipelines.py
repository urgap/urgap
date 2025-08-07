"""Pipeline Proposer."""

import contextlib
import logging
import sys

import networkx as nx

from pyvis.network import Network

import urgap

logger = logging.getLogger(__name__)


def main(source_uftype: str, target_uftype: str) -> None:
    """Propose execution graphs for given source_uftype and target_uftype.

    Args:
        source_uftype (str Urgap uftype): From which data type
        target_uftype (str Urgap uftype): To which data type

    E.g.

    python propose_pipelines.py ".thermo.raw" ".peptideforest.csv"
    """
    graph = nx.DiGraph()

    for unode_name in urgap.instances.unode_manager.wrapper_lookup:
        unode_class = urgap.init_node(unode_name)
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

    nodes_in_subgraph = set()
    for one_possible_path in nx.all_simple_paths(
        graph,
        source=source_uftype,
        target=target_uftype,
    ):
        nodes_in_subgraph |= set(one_possible_path)
    msg = (
        f"Found {len(nodes_in_subgraph)} nodes from {source_uftype} to {target_uftype}"
    )
    logger.info(msg)
    subgraph = graph.subgraph(list(nodes_in_subgraph))
    net = Network(
        height="750px",
        width="100%",
        directed=True,
    )
    net.from_nx(subgraph)
    net.show_buttons(filter_=["layout", "physics"])
    net.show("proposed_pipelines.html")
    logger.info("Wrote Proposed_pipelines.html")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])