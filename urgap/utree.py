
import types

import networkx as nx
import networkx.classes.digraph



class UTreeQuerier:

    """

        """Build a directed graph from a file providing namespacing.

        Args:
            namespace: Provides the namespace which is basis for the edges.

        Note:
        """
        if namespace is None:
            namespace = namespace.__dict__
            parent_node = "ANY"

        for key, value in namespace.items():
            else:
                continue
            if parent_node == "ANY":
                new_node_name = key
            else:
                new_node_name = parent_node.replace(".ANY", "") + "." + key
            if new_node_name[-1].islower():
                new_node_name += ".ANY"
            if isinstance(value, types.SimpleNamespace):

        general_types = self.get_leafs_from_node(node="any.ANY")
        for leaf, ext in general_types:
            for node in leafs_with_ext:

    def get_nodes_with_ext(self, ext: str) -> list:

        Args:

        Returns:
        """
        return [x for x, y in self.G.nodes(data=True) if y.get("ext", "").endswith(ext)]

    def get_subgraph(self, node: str) -> networkx.classes.digraph.DiGraph:

        Args:

        Returns:
        """
        return nx.ego_graph(self.G, node, radius=100)

    def get_leafs_from_node(self, node: str) -> list:

        Args:
            node: Name of the query node.

        Returns:
        """
        try:
                (x, self.G.nodes[x]["ext"])
                for x, deg in self.get_subgraph(node).out_degree()
                if deg == 0
            ]
        except KeyError as e:

    def to_root(self, node: str) -> list:

        Args:
            node: Name of the query node.

        Returns:
        """
        try:
                (node, self.G.nodes[node]["ext"])
                for node in nx.dfs_tree(
                ).nodes
        except KeyError as e: