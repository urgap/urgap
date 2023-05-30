import logging
from pprint import pformat
from plotly.offline import init_notebook_mode, iplot



class UReport:

    def __init__(
        self,

        Args:
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
        if self._umeta is None:
        return self._umeta


        """

        return f"""
UReport id {id(self)}


    {self.umeta}
        """

    @property

        Returns:
        """

    @property

        Returns:
        """

    @property

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


        return self.umeta.umeta_exists(reference_ufile)

        node_name = self.umeta.urun_dict["unode_rinfo"]["meta_info"]["name"]

        init_notebook_mode(connected=True)
            self.node_aliases[i] = node
        fig = go.Figure(
            layout=go.Layout(
                title="Simplified DAG with aliases",
                showlegend=False,
                hovermode="closest",
            ),
        )

        fig.update_layout(template="simple_white")
        iplot(fig)


        Args:

        Returns:
        """
        translated_aliases = {
            self.node_aliases[alias]: value for alias, value in nodes.items()
        }
                if len(requested_uftypes) == 0:
                    query_results += ut.output_files
                else:
        return query_results