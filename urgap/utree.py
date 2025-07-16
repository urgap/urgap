"""UTreeQuerier module of urgap2."""

import types

import networkx as nx
import networkx.classes.digraph

import urgap


class UTreeQuerier:
    """Urgap UTreeQuerier class.

    Queries an urgap type networkx tree.
    """

    def __init__(
        self,
        namespace: str | None = None,
        graph: nx.DiGraph | None = None,
        parent_node: str | None = None,
    ) -> None:
        """Build a directed graph from a file providing namespacing.

        Args:
            namespace: Provides the namespace which is basis for the edges.
            graph: Graph to use as basis.
            parent_node: Parent node of the graph.

        Note:
            Usage examples:
                - python -c "import urgap; print(urgap.instances.utree_querier.get_nodes_with_ext('.csv'))"
                - python -c "import urgap; print(urgap.instances.utree_querier.get_subgraph('dbsearch.ANY').nodes(data=True))"
        """
        if namespace is None:
            namespace = urgap.uftypes
        if isinstance(namespace, types.ModuleType | types.SimpleNamespace):
            namespace = namespace.__dict__
        if graph is None:
            graph = nx.DiGraph()
            graph.add_node("ANY", ext=".ANY")
        if parent_node is None:
            parent_node = "ANY"
        self.G = self._walk_tree(namespace, graph=graph, parent_node=parent_node)
        self.G = self._connect_general_types(self.G)
        self.G = self._connect_tabular_types(self.G)

    def _walk_tree(
        self,
        namespace: dict,
        graph: nx.DiGraph | None = None,
        parent_node: str | None = None,
    ) -> nx.DiGraph:
        """Walk the namespace recursively to construct the graph.

        Args:
            namespace: Namespace as a dictionary.
            graph: NetworkX directed graph.
            parent_node: Parent node name.

        Returns:
            The constructed graph.
        """
        for key, value in namespace.items():
            if (
                not isinstance(key, types.SimpleNamespace | str)
                or key == "ANY"
                or key.startswith("_")
            ):
                continue
            if isinstance(value, types.SimpleNamespace):
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
                graph = self._walk_tree(
                    value.__dict__,
                    graph,
                    parent_node=new_node_name,
                )
        return graph

    def _connect_general_types(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Connect general types within the graph.

        Args:
            graph: NetworkX directed graph.

        Returns:
            Modified graph with general types connected.
        """
        general_types = self.get_leafs_from_node(node="any.ANY")
        for leaf, ext in general_types:
            leaf_ext = "." + ext.split(".")[-1]
            leafs_with_ext = set(self.get_nodes_with_ext(ext=leaf_ext)).difference(
                {leaf},
            )
            for node in leafs_with_ext:
                graph.add_edge(leaf, node)
        return graph

    def _connect_tabular_types(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Connect tabular file types as children of any.TABULAR.

        Args:
            graph: NetworkX directed graph.

        Returns:
            Modified graph with tabular types connected.
        """
        for leaf in ["any.CSV", "any.XLSX", "any.PARQUET"]:
            graph.add_edge("any.TABULAR", leaf)
        return graph

    def get_nodes_with_ext(self, ext: str) -> list:
        """Find nodes with a provided extension.

        Args:
            ext: Extension string to search for (e.g. ".csv").

        Returns:
            List of nodes (uftypes) with the given extension.
        """
        return [x for x, y in self.G.nodes(data=True) if y.get("ext", "").endswith(ext)]

    def get_subgraph(self, node: str) -> networkx.classes.digraph.DiGraph:
        """Get a subgraph containing nodes within 100 steps of a specified node.

        Args:
            node: Node from which to build the subgraph.

        Returns:
            Subgraph centered around the specified node.
        """
        return nx.ego_graph(self.G, node, radius=100)

    def get_leafs_from_node(self, node: str) -> list:
        """Get all leaf nodes (with out-degree 0) connected to a node.

        Args:
            node: Name of the query node.

        Returns:
            List of tuples (node_name, extension) for all leafs.

        Raises:
            KeyError: If the node is missing in the tree.
        """
        try:
            return [
                (x, self.G.nodes[x]["ext"])
                for x, deg in self.get_subgraph(node).out_degree()
                if deg == 0
            ]
        except KeyError as e:
            msg = f"Node {e.args[0]} is missing in uftype tree"
            raise KeyError(msg) from e

    def to_root(self, node: str) -> list:
        """Get the node and all its parents up to the root of the tree.

        Args:
            node: Name of the query node.

        Returns:
            List of tuples (node_name, extension) for the node and its parents.

        Raises:
            KeyError: If the node is missing in the tree.
        """
        try:
            return [
                (node, self.G.nodes[node]["ext"])
                for node in nx.dfs_tree(
                    self.G.reverse(),
                    source=self.get_nodes_with_ext(ext=node)[0],
                ).nodes
            ]
        except KeyError as e:
            msg = f"Node {e.args[0]} is missing in uftype tree"
            raise KeyError(msg) from e

    def get_uftype_or_closest_any(self, suffixes: list) -> str:
        """Get uftypes or closest any from tree given a list of suffixes.

        Args:
            suffixes (list): list of suffixes

        Returns:
            str: uftype of closest any uftype.
        """
            suffixes = suffixes[-2:]
        possible_uftypes = self.get_nodes_with_ext("".join(suffixes))
        if len(possible_uftypes) == 1:
            uftype = possible_uftypes[0]
        else:
            possible_uftypes = urgap.instances.utree_querier.get_nodes_with_ext(
                suffixes[-1],
            )
            if len(possible_uftypes) == 1:
                uftype = possible_uftypes[0]
            else:
                for _ in possible_uftypes:
                    if _.startswith("any"):
                        uftype = _
                        break
        return "." + uftype