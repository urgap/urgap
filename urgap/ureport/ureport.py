
import json
import logging
from collections import defaultdict
from pathlib import Path
from pprint import pformat

import networkx as nx
import plotly.graph_objects as go
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
        self._traces = {}
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


        Returns:
        """
                )
                wid=wid,
            )

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

    def walk(
        self,
        wid: str,
        graph: nx.DiGraph,
    ) -> nx.DiGraph:

        Args:

        Returns:
        """


            for ofile in ut.output_files:
                graph.add_edge(
                    weight=4.7,
                    arrow=True,
                )

            for ifile in ut.input_files:
                graph.add_edge(
                    weight=4.7,
                    arrow=True,
                )

                    graph = self.walk(
                        wid=wid,
                        graph=graph,
                    )
        return graph

    def was_skipped(
        self,
        wid: str,
    ) -> bool:
        """Check if a run was skipped.

        Args:

        Returns:
        """

    def was_run(
        self,
        wid: str,
    ) -> bool:
        """Check if a run was executed.

        Args:

        Returns:
        """

    def crashed(
        self,
        wid: str,
    ) -> bool:
        """Check if a run crashed.

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

    def summary(self) -> dict:

        Returns:
        """
        summary = {}

            }
        return summary



        Returns:
        """
        reverse_graph = self.graph.reverse()
        root_nodes = set()
        visited_nodes = set()

            if node in visited_nodes:
            visited_nodes.add(node)
            if self.graph.in_degree(node) == 0:
                root_nodes.add(node)

            for neighbor in reverse_graph.neighbors(node):
            return root_nodes


    def generate_report(self) -> list:

        Returns:
        """
        wid = ",".join(self.wids)
        data = [
            {
                "section_title": "Data lineage overview",
                "networks": [],
                "figures": [],
                "tables": [],
        ]
        history = {
            "title": "Execution times",
            "caption": f"History of execution times for {wid}",
            "rows": [],
        }
        urd_overview = {
            "title": "Run Parameters HL overview",
            "caption": f"URun dict information for workflow ID {wid}",
            "headers": [
                "input_files",
                "output_files",
                "version",
            ],
            "rows": [],
        }
        execution_graph = {
            "the magma color palette and scaled according to execution time. "
            "Purple arrows indicate incoming data and green arrows"
            " point to data produced. Use scroll wheel to zoom.",
            "links": [],
            "nodes": [],
        }
        already_seen_nodes = set()
            ).total_seconds()
            execution_graph["nodes"].append(
                {
                    "id": "process",
                    "processing_time": processing_time,
            )
            history["rows"].append(
                {
                    "Node": ut.unode_meta["name"],
                    "processing time [s]": processing_time,
            )
            urd_overview["rows"].append(
                {
                    "version": ut.urun_dict["version"],
            )
            for ufile in ut.input_files:
                execution_graph["links"].append(
                    {
                        "source": source,
                        "value": 1,
                        "type": "incoming",
                )
                if source not in already_seen_nodes:
                    execution_graph["nodes"].append({"name": source, "id": "data"})
                    already_seen_nodes.add(source)
            for ufile in ut.output_files:
                execution_graph["links"].append(
                    {
                        "target": target,
                        "value": 1,
                        "type": "outgoing",
                )
                if target not in already_seen_nodes:
                    execution_graph["nodes"].append({"name": target, "id": "data"})
                    already_seen_nodes.add(target)

        execution_graph["links"] = json.dumps(execution_graph["links"])
        execution_graph["nodes"] = json.dumps(execution_graph["nodes"])
        data[0]["networks"].append(execution_graph)
        data[0]["tables"] += [history, urd_overview]
        return data

    def render_report(
    ) -> None:

        Args:
        """
        data = self.generate_report()

        template_folder = Path(__file__).parent / "templates"
        env = Environment(
        )
        template = env.get_template(template_name)
        html_out = template.render(
            version="0.7.0",
            data=data,
        )
            print(html_out, file=oo)