
import types

import networkx as nx
import networkx.classes.digraph



class UTreeQuerier:

    """

    def __init__(
        self,
        namespace: str | None = None,
        graph: nx.DiGraph | None = None,
        parent_node: str | None = None,
        """Build a directed graph from a file providing namespacing.

        Args:
            namespace: Provides the namespace which is basis for the edges.
            graph: Graph to use as basis.
            parent_node: Parent node of the graph.

        Note:
        """
        if namespace is None:
            namespace = namespace.__dict__
        if graph is None:
            graph = nx.DiGraph()
            graph.add_node("ANY", ext=".ANY")
        if parent_node is None:
            parent_node = "ANY"
        self.G = self._walk_tree(namespace, graph=graph, parent_node=parent_node)
        self.G = self._connect_general_types(self.G)
        self.G = self._connect_tabular_types(self.G)

        for key, value in namespace.items():
                continue
                extension = parent_node.replace("ANY", "") + key + ".ANY"
            elif isinstance(value, str):
                extension = value
            else:
                continue
            if parent_node == "ANY":
                new_node_name = key
            else:
                new_node_name = parent_node.replace(".ANY", "") + "." + key
            if new_node_name[-1].islower():
                new_node_name += ".ANY"
            graph.add_node(new_node_name, ext=extension)
            graph.add_edge(parent_node, new_node_name)
            if isinstance(value, types.SimpleNamespace):
        return graph

        general_types = self.get_leafs_from_node(node="any.ANY")
        for leaf, ext in general_types:
            for node in leafs_with_ext:
                graph.add_edge(leaf, node)
        return graph

        for leaf in ["any.CSV", "any.XLSX", "any.PARQUET"]:
            graph.add_edge("any.TABULAR", leaf)
        return graph

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