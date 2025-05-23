
from __future__ import annotations

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
        ucfs: str | None = None,
        wid: str | None = None,
        storage_base_uri: str | None = None,
        umeta_io: str | None = None,
    ) -> None:

        Args:
            ufile: UFile associated with report.
            ucfs: Object associated with report.
            wid: Workflow ID.
            storage_base_uri: Storage base UUri, where to find the referenced UFiles.
        """
        self._umeta = None
        self._os = []
        self.node_aliases = {}
        self._traces = {}
        self.storage_base_uri = storage_base_uri
        if umeta_io is None:
        self.umeta_io = umeta_io

        if ufile is not None:
            if ucfs is not None:
                msg = "You cannot define ufile and ucfs to initialize a report"
                raise KeyError(msg)
            ucfs = ufile.ucfs
        if ucfs is not None:
                # is first file
                self._os.append(ucfs)

            self.execution_history = {}
                    self.execution_history[key] = history
        else:
            self.execution_history = self.umeta.load_history(
            )

    @property
        """Get umeta interface.

        Returns:
        """
        if self._umeta is None:
        return self._umeta

    def get_trace(
        """Get UTrace object for a specific node execution and workflow.

        Args:
            wid: Workflow ID.
            storage_base_uri: Optionally override storage base UUri.

        Returns:
            UTrace object.
        """
                missing_history = self.umeta.load_history(
                )
                self._merge_histories(other_history=missing_history)
                wid=wid,
                storage_base_uri=storage_base_uri,
            )

    def __repr__(self) -> str:
        """Return a user-friendly UReport overview string.

        Returns:
            String with summary of the UReport instance.
        """
        return f"""
UReport id {id(self)}

self.history:
{pformat(self.execution_history, sort_dicts=True, indent=4)}

UMeta:
    {self.umeta}
        """

    @property
    def wids(self) -> set:
        """Get all WIDs of currently loaded UTraces.

        Returns:
            Set of WIDs.
        """
        return {w for n, w in self.execution_history}

    @property

        Returns:
            Set of node execution IDs.
        """
        return {n for n, w in self.execution_history}

    @property
    def graph(self) -> nx.DiGraph:
        """Get internal directed graph representing execution DAG.

        Returns:
            NetworkX directed graph object.
        """
        graph = nx.DiGraph()
        for missing_node in self._os:
            graph.add_node(missing_node)
                continue
            graph = self.walk(
                wid=wid,
                storage_base_uri=self.storage_base_uri,
                graph=graph,
            )
        return graph

    def walk(
        self,
        wid: str,
        graph: nx.DiGraph,
        storage_base_uri: str | None = None,
    ) -> nx.DiGraph:
        """Build up the execution graph recursively for all input/output files.

        Args:
            wid: Workflow ID.
            graph: Existing graph object.
            storage_base_uri: Optionally override storage base UUri.

        Returns:
            Updated graph object.
        """


            for ofile in ut.output_files:
                graph.add_edge(
                    ofile.ucfs,
                    weight=4.7,
                    arrow=True,
                )

            for ifile in ut.input_files:
                graph.add_edge(
                    ifile.ucfs,
                    weight=4.7,
                    arrow=True,
                )

                )
                    hi2 = self.umeta.load_history(
                    )
                    self._merge_histories(other_history=hi2)
                    exe_id, wid = next(iter(hi2))
                    graph = self.walk(
                        wid=wid,
                        graph=graph,
                        storage_base_uri=storage_base_uri,
                    )
                    raise OSError(msg)
        return graph

    def _merge_histories(self, other_history: dict) -> None:
        """Merge execution histories with possible timestamp update.

        Args:
            other_history: Another execution history dictionary to merge.
        """
        for other_key, other_value in other_history.items():
            if other_key not in self.execution_history:
                self.execution_history[other_key] = other_value
            elif (
                > self.execution_history[other_key]["started_time"]
            ):
                msg = f"Overwriting entry for {other_key} with newer timestamp"
                self.execution_history[other_key] = other_value

    def was_skipped(
        self,
        wid: str,
    ) -> bool:
        """Check if a run was skipped.

        Args:
            wid: Workflow ID.

        Returns:
            True if the trace was skipped, else False.
        """

    def was_run(
        self,
        wid: str,
    ) -> bool:
        """Check if a run was executed.

        Args:
            wid: Workflow ID.

        Returns:
            True if the trace was run, else False.
        """

    def crashed(
        self,
        wid: str,
    ) -> bool:
        """Check if a run crashed.

        Args:
            wid: Workflow ID.

        Returns:
            True if the trace crashed, else False.
        """

    def data_exists(self) -> bool:
        """Check if file object exists in storage.

        Returns:
            True if data exists, else False.
        """
        return self.ufile.remote_object_exists()

        """Check if meta data file object exists.

        Args:
            reference_ufile: UFile to check.

        Returns:
            True if meta data exists, else False.
        """
        return self.umeta.umeta_exists(reference_ufile)

    def generate_node_vis(self) -> list:
        """Generate node-specific data visualization.

        Returns:
            List of visualizations.
        """
        node_name = self.umeta.urun_dict["unode_rinfo"]["meta_info"]["name"]

    def draw_execution_dag(self) -> None:
        """Generate and display a DAG of execution described by UReport, with node aliases."""
        init_notebook_mode(connected=True)
        nodes, links = self._get_history_nodes_and_links()
        custom_hover_data = []
        for i, node in enumerate(nodes):
            custom_hover_data.append(f"<b>UNodeExeID:</b> {node}<br><b>Alias:</b> {i}")
            self.node_aliases[i] = node
        sources = []
        targets = []
        colors = []
        shortened_nodes = []
        for source, target in links:
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
                    node={
                        "pad": 15,
                        "thickness": 20,
                        "line": {"color": "black", "width": 0.5},
                        "label": shortened_nodes,
                        "color": colors,
                        "customdata": custom_hover_data,
                        "hovertemplate": "%{customdata}<extra></extra>",
                    },
                    link={
                        "arrowlen": 15,
                        "source": sources,
                        "target": targets,
                        "value": list(links.values()),
                    },
            ],
            layout=go.Layout(
                title="Simplified DAG with aliases",
                showlegend=False,
                hovermode="closest",
                margin={"b": 20, "l": 5, "r": 5, "t": 40},
                xaxis={
                    "showgrid": False,
                    "zeroline": False,
                    "showticklabels": False,
                    "visible": False,
                },
                yaxis={
                    "showgrid": False,
                    "zeroline": False,
                    "showticklabels": False,
                    "visible": False,
                },
            ),
        )

        fig.update_layout(template="simple_white")
        iplot(fig)

    def _get_history_nodes_and_links(self) -> tuple:
        """Get nodes and their links from execution history.

        Returns:
            Tuple containing list of nodes and dictionary of links.
        """
        non_root_ufiles = set()
            ut = self.get_trace(
            )
            for ufile in ut.output_files:
                non_root_ufiles.add(ufile.ucfs)
        nodes = []
        exact_sources_to_nodes = defaultdict(set)
        links = defaultdict(int)
            ut = self.get_trace(
            )
            for ufile in ut.input_files:
                new_connection = 1
                    new_connection = 0
                else:
                nodes, source = self._append_ufile_source(
                )
        return nodes, links

    def _append_ufile_source(
    ) -> tuple:
        """Append object source name to nodes.

        Args:
            ufile: UFile to get object name from.
            non_root_ufiles: Output ufiles.
            nodes: List of node exe IDs and object names.

        Returns:
            Tuple of updated nodes list and the source name of the ufile.
        """
        if ufile.ucfs in non_root_ufiles:
            source = ufile.ucfs
        else:
            source = "<" + ufile.uftype + ">"
        if source not in nodes:
            nodes.append(source)
        return nodes, source


        Args:
            nodes: Dictionary with node alias (int) as key and list of requested output uftypes as value.
                Leave list empty to request all output uftypes.

        Returns:
            UFileList of requested output files.
        """
        translated_aliases = {
            self.node_aliases[alias]: value for alias, value in nodes.items()
        }
            ut = self.get_trace(
                wid=wid,
                storage_base_uri=self.storage_base_uri,
            )
                if len(requested_uftypes) == 0:
                    query_results += ut.output_files
                else:
                    query_results.extend(
                        output_ufile
                        for output_ufile in ut.output_files
                        if output_ufile.uftype in requested_uftypes
                    )
        return query_results

    def summary(self) -> dict:
        """Create a basic text summary of execution.

        Returns:
            Dictionary with summary details for each node execution.
        """
        summary = {}

                "execution_time": self.execution_history.execution_time(
                ),
            }
        return summary

    def find_root_files(self, target_node: str) -> list | None:
        """Find the root files for a given node.

        Args:
            target_node: Node to search for root files.

        Returns:
            List of graph node names representing root files, or None.
        """
        reverse_graph = self.graph.reverse()
        root_nodes = set()
        visited_nodes = set()

        def get_root_nodes(
        ) -> list | None:
            if node in visited_nodes:
                return None
            visited_nodes.add(node)
            if self.graph.in_degree(node) == 0:
                root_nodes.add(node)

            for neighbor in reverse_graph.neighbors(node):
                root_nodes = get_root_nodes(
                )
            return root_nodes

        return get_root_nodes(target_node, reverse_graph, visited_nodes, root_nodes)

    def generate_report(self) -> list:
        """Create a JSON-compatible report for this pipeline execution.

        Returns:
            List with report structure as JSON-serializable data.
        """
        node_id_header = "Node ID"
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
            "headers": ["Node", node_id_header, "processing time [s]"],
            "rows": [],
        }
        urd_overview = {
            "title": "Run Parameters HL overview",
            "caption": f"URun dict information for workflow ID {wid}",
            "headers": [
                node_id_header,
                "input_files",
                "output_files",
                "version",
            ],
            "rows": [],
        }
        execution_graph = {
            "title": "Execution graph",
            "the magma color palette and scaled according to execution time. "
            "Purple arrows indicate incoming data and green arrows"
            " point to data produced. Use scroll wheel to zoom.",
            "links": [],
            "nodes": [],
        }
        already_seen_nodes = set()
            ut = self.get_trace(
            )
            processing_time = ut.history.execution_time(
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
                    "input_files": [x.ucfs for x in ut.input_files],
                    "output_files": [x.ucfs for x in ut.output_files],
            )
            for ufile in ut.input_files:
                source = ufile.ucfs
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
                target = ufile.ucfs
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
        """Render the pipeline report as an HTML file using Jinja2 templates.

        Args:
            output_path: Path to the output file.
            template_name: Name of the template (only "basic.html" currently supported).
        """
        data = self.generate_report()
        from jinja2 import Environment, FileSystemLoader

        template_folder = Path(__file__).parent / "templates"
        env = Environment(
        )
        template = env.get_template(template_name)
        html_out = template.render(
            version="0.7.0",
            data=data,
        )
            print(html_out, file=oo)
        msg = f"Writing report to {output_path}"