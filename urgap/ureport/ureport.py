import logging
from collections import defaultdict
from pprint import pformat
import networkx as nx
from plotly.offline import init_notebook_mode, iplot



class UReport:

    def __init__(
        self,

        Args:
            wid: Workflow ID.
        """
        self._umeta = None
        self._os = []
        self.node_aliases = {}
        if umeta_io is None:
        self.umeta_io = umeta_io

        if ufile is not None:
                raise KeyError(msg)
                # is first file

        else:

    @property

        Returns:
        """
        if self._umeta is None:
        return self._umeta


        """

        return f"""
UReport id {id(self)}


    {self.umeta}
        """

    @property
    def wids(self) -> set:

        Returns:
        """

    @property

        Returns:
        """

    @property
    def graph(self) -> nx.DiGraph:

        Returns:
        """
        graph = nx.DiGraph()
        for missing_node in self._os:
            graph.add_node(missing_node)
                continue
            graph = self.walk(
                wid=wid,
                graph=graph,
            )
        return graph


        Args:

        Returns:
        """

                graph.add_edge(
                    weight=4.7,
                    arrow=True,
                )

                graph.add_edge(
                    weight=4.7,
                    arrow=True,
                )

                    graph = self.walk(
                        wid=wid,
                        graph=graph,
                    )
        return graph


        Args:

        Returns:
        """

    def data_exists(self) -> bool:

        Returns:
            True if data exists, else False.
        """

        """Check if meta data file object exists.

        Args:
            reference_ufile: UFile to check.

        Returns:
            True if meta data exists, else False.
        """
        return self.umeta.umeta_exists(reference_ufile)

        node_name = self.umeta.urun_dict["unode_rinfo"]["meta_info"]["name"]

        init_notebook_mode(connected=True)
        custom_hover_data = []
        for i, node in enumerate(nodes):
            custom_hover_data.append(f"<b>UNodeExeID:</b> {node}<br><b>Alias:</b> {i}")
            self.node_aliases[i] = node
        sources = []
        targets = []
        colors = []
        shortened_nodes = []
            sources.append(source)
            targets.append(target)
        for node in nodes:
            if node.startswith("<"):
                colors.append("orange")
                shortened_nodes.append(node)
            else:
                colors.append("blue")
                shortened_nodes.append(node.rsplit("_", 2)[0])

        fig = go.Figure(
            data=[
                go.Sankey(
            ],
            layout=go.Layout(
                title="Simplified DAG with aliases",
                showlegend=False,
                hovermode="closest",
            ),
        )

        fig.update_layout(template="simple_white")
        iplot(fig)


        Args:
                Leave list empty to request all output uftypes.

        Returns:
        """
        translated_aliases = {
            self.node_aliases[alias]: value for alias, value in nodes.items()
        }
                if len(requested_uftypes) == 0:
                    query_results += ut.output_files
                else:
        return query_results