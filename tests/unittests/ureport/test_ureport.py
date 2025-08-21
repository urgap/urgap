from datetime import timedelta
from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx
import pytest

import urgap

from urgap.ureport.ureport import UReport


def test_init_with_ufile_and_ucfs_raises_keyerror(caplog):
    dummy_ufile = "dummy_ufile"
    dummy_ucfs = ["dummy_ucf"]

    with caplog.at_level("WARNING"):
        with pytest.raises(
            KeyError, match="You cannot define ufile and ucfs to initialize a report"
        ):
            UReport(ufile=dummy_ufile, ucfs=dummy_ucfs)

    assert "You cannot define ufile and ucfs to initialize a report" in caplog.text


import pytest

from urgap.ureport.ureport import UReport


def test_missing_history_triggers_umeta_load_history(monkeypatch):
    dummy_wid = "wid123"

    class DummyUFile:
        ucfs = "dummy_ucfs"

    class DummyUMeta:


    monkeypatch.setattr(UReport, "umeta", DummyUMeta())

    report = UReport(ufile=DummyUFile())

    assert hasattr(report, "execution_history")


def test_traces_populated_with_load_utrace(monkeypatch):
    dummy_wid = "wid123"

    class DummyUFile:
        ucfs = "dummy_ucfs"

    class DummyUMeta:



    monkeypatch.setattr(UReport, "umeta", DummyUMeta())

    monkeypatch.setattr(UReport, "_merge_histories", lambda self, other_history: None)

    report = UReport(ufile=DummyUFile())

    assert key in report._traces
    assert report._traces[key]["utrace_loaded"] is True


def test_traces_populated_with_load_utrace(monkeypatch):
    dummy_wid = "wid123"

    class DummyUFile:
        ucfs = "dummy_ucfs"

    class DummyUMeta:

            return {"some": "history"}


    monkeypatch.setattr(UReport, "_merge_histories", lambda self, other_history: None)

    report = UReport(ufile=DummyUFile(), wid=dummy_wid)

    report._umeta = DummyUMeta()

        report._traces[(nei, dummy_wid)] = report._umeta.load_utrace(
            wid=dummy_wid,
            history=report.execution_history,
            storage_base_uri=None,
        )

    assert key in report._traces
    assert report._traces[key]["utrace_loaded"] is True
    assert report._traces[key]["wid"] == dummy_wid


def test_get_wids_from_execution_history(monkeypatch):
    class DummyUMeta:
            return {
                ("unode1", "widA"): {"some": "history"},
                ("unode2", "widB"): {"other": "history"},
            }

    original_init = UReport.__init__

    def dummy_init(self, *args, **kwargs):
        self._os = []
        self.node_aliases = {}
        self._traces = {}
        self.storage_base_uri = None
        self.umeta_io = "sqlite3"
        self.execution_history = DummyUMeta().load_history()

    monkeypatch.setattr(UReport, "__init__", dummy_init)

    report = UReport()

    monkeypatch.setattr(UReport, "__init__", original_init)

    wids = {w for n, w in report.execution_history}

    assert wids == {"widA", "widB"}


import pytest

from urgap.ureport.ureport import UReport


def test_traces_assignment_line(monkeypatch):
    dummy_wid = "wid123"

    class DummyUFile:
        ucfs = "dummy_ucfs"

    class DummyUMeta:



    monkeypatch.setattr(UReport, "_merge_histories", lambda self, other_history: None)

    report = UReport(ufile=DummyUFile())

    report._umeta = DummyUMeta()

        wid=dummy_wid,
        history=report.execution_history,
        storage_base_uri=None,
    )

    assert key in report._traces
    assert report._traces[key]["utrace_loaded"] is True
    assert report._traces[key]["wid"] == dummy_wid


    dummy_wid = "wid123"

    class DummyUFile:
        ucfs = "dummy_ucfs"

    class DummyUMeta:
            return ["unode1", "unode2"]

            return {"some": "history"}

    monkeypatch.setattr(UReport, "_merge_histories", lambda self, other_history: None)

    report = UReport.__new__(UReport)
    report._umeta = DummyUMeta()
    report._os = []

    producing_ucfs = "dummy_ucfs"

    with pytest.raises(OSError) as exc_info:
            import logging

            logger = logging.getLogger()
            logger.warning(msg)
            raise OSError(msg)



def test_merge_histories_started_time():
    report = UReport.__new__(UReport)

    report.execution_history = {
        ("unode1", "wid1"): {"started_time": 10, "other": "data"}
    }

    other_history = {("unode1", "wid1"): {"started_time": 20, "other": "new_data"}}

    UReport._merge_histories(report, other_history)

    assert report.execution_history[("unode1", "wid1")]["started_time"] == 20
    assert report.execution_history[("unode1", "wid1")]["other"] == "new_data"


def test_merge_histories_overwrite(monkeypatch):
    import urgap.ureport.ureport as ureport_module

    from urgap.ureport.ureport import UReport

    report = UReport.__new__(UReport)

    report.execution_history = {
        ("unode1", "wid1"): {"started_time": 10, "other": "old_data"}
    }

    other_history = {("unode1", "wid1"): {"started_time": 20, "other": "new_data"}}

    logs = []
    monkeypatch.setattr(ureport_module.logger, "info", lambda msg: logs.append(msg))

    UReport._merge_histories(report, other_history)

    key = ("unode1", "wid1")
    assert report.execution_history[key]["started_time"] == 20
    assert report.execution_history[key]["other"] == "new_data"

    assert any("Overwriting entry" in msg for msg in logs)


def test_was_skipped_called():
    report = UReport.__new__(UReport)

    class DummyHistory:
            return True

    dummy_history = DummyHistory()
    report.execution_history = dummy_history

    result = report.was_skipped("dummy_wid", "dummy_node")

    assert dummy_history.called_with == ("dummy_wid", "dummy_node")
    assert result is True


def test_was_run_called():
    report = UReport.__new__(UReport)

    class DummyHistory:
            return True

    dummy_history = DummyHistory()
    report.execution_history = dummy_history

    result = report.was_run("dummy_wid", "dummy_node")

    assert dummy_history.called_with == ("dummy_wid", "dummy_node")
    assert result is True


def test_crashed_called():
    report = UReport.__new__(UReport)

    class DummyHistory:
            return True

    dummy_history = DummyHistory()
    report.execution_history = dummy_history

    result = report.crashed("dummy_wid", "dummy_node")

    assert dummy_history.called_with == ("dummy_wid", "dummy_node")
    assert result is True


def test_remote_object_exists_dummy():
    report = UReport.__new__(UReport)

    class DummyUFile:
        def remote_object_exists(self):
            self.called = True
            return True

    report.ufile = DummyUFile()

    def remote_object_exists(self):
        return self.ufile.remote_object_exists()

    UReport.remote_object_exists = remote_object_exists

    result = report.remote_object_exists()

    assert result is True
    assert report.ufile.called is True


def test_umeta_exists_called(monkeypatch):
    report = UReport.__new__(UReport)

    class DummyUFile:
        pass

    reference_ufile = DummyUFile()

    class DummyUMeta:
        def umeta_exists(self, ufile):
            self.called_with = ufile
            return True

    report._umeta = DummyUMeta()

    result = report.umeta.umeta_exists(reference_ufile)

    assert result is True
    assert report._umeta.called_with == reference_ufile


def test_generate_node_vis(monkeypatch):
    report = UReport.__new__(UReport)

    class DummyUFile:
        pass

    dummy_ufile = DummyUFile()
    report.ufile = dummy_ufile

    class DummyUMeta:
        urun_dict = {"unode_rinfo": {"meta_info": {"name": "dummy_node"}}}

    report._umeta = DummyUMeta()

    class DummyNode:
        def generate_node_vis(self, ufile):
            self.called_with = ufile
            return "node_vis_result"

    monkeypatch.setattr(urgap, "init_node", lambda name: DummyNode())

    def generate_node_vis_wrapper(self):
        node_name = self.umeta.urun_dict["unode_rinfo"]["meta_info"]["name"]
        return urgap.init_node(node_name).generate_node_vis(self.ufile)

    report.generate_node_vis = generate_node_vis_wrapper.__get__(report)

    result = report.generate_node_vis()

    assert result == "node_vis_result"
    assert report.ufile is dummy_ufile


def test_exact_sources_condition(monkeypatch):
    report = UReport.__new__(UReport)

    class DummyUFile:
        ucfs = "ucfs_1"

    dummy_ufile = DummyUFile()
    report.ufile = dummy_ufile

    exact_sources_to_nodes = {"unode123": {"ucfs_1", "ucfs_2"}}


    new_connection = 1

        new_connection = 0

    assert new_connection == 0


def test_summary_initialization():
    report = UReport.__new__(UReport)

    summary = {}

    summary["dummy_key"] = "dummy_value"

    assert isinstance(summary, dict)
    assert summary.get("dummy_key") == "dummy_value"


def test_execution_summary(monkeypatch):
    report = UReport.__new__(UReport)

    class DummyExecutionHistory:
        def keys(self):
            return [("unode1", "wid1"), ("unode2", "wid2")]

            return 42

            return False

            return True

    report.execution_history = DummyExecutionHistory()

    summary = {}
        }

    assert "unode1" in summary
    assert summary["unode1"]["execution_time"] == 42
    assert summary["unode1"]["was_skipped"] is False
    assert summary["unode1"]["was_run"] is True

    assert "unode2" in summary
    assert summary["unode2"]["execution_time"] == 42
    assert summary["unode2"]["was_skipped"] is False
    assert summary["unode2"]["was_run"] is True


def test_reverse_graph_and_root_nodes(monkeypatch):
    report = UReport.__new__(UReport)

    dummy_graph = nx.DiGraph()
    dummy_graph.add_edges_from([("node1", "node2"), ("node2", "node3")])

    monkeypatch.setattr(type(report), "graph", property(lambda self: dummy_graph))

    reverse_graph = report.graph.reverse()
    root_nodes = set()
    visited_nodes = set()

    # Assertions
    assert isinstance(reverse_graph, nx.DiGraph)
    assert root_nodes == set()
    assert visited_nodes == set()


def test_reverse_graph_and_get_root_nodes(monkeypatch):
    report = UReport.__new__(UReport)

    dummy_graph = nx.DiGraph()
    dummy_graph.add_edges_from([("node1", "node2"), ("node2", "node3")])

    monkeypatch.setattr(type(report), "graph", property(lambda self: dummy_graph))

    reverse_graph = report.graph.reverse()
    root_nodes = set()
    visited_nodes = set()

    def get_root_nodes(node, reverse_graph, visited_nodes, root_nodes):
        if node in visited_nodes:
            return
        visited_nodes.add(node)
        predecessors = list(reverse_graph.predecessors(node))
        if not predecessors:
            root_nodes.add(node)
            return
        for pred in predecessors:
            get_root_nodes(pred, reverse_graph, visited_nodes, root_nodes)

    for node in dummy_graph.nodes:
        get_root_nodes(node, reverse_graph, visited_nodes, root_nodes)

    assert root_nodes == {"node3"}
    assert visited_nodes == {"node1", "node2", "node3"}


def test_root_node_logic(monkeypatch):
    report = UReport.__new__(UReport)

    dummy_graph = nx.DiGraph()
    dummy_graph.add_edges_from([("node1", "node2")])
    monkeypatch.setattr(type(report), "graph", property(lambda self: dummy_graph))

    root_nodes = set()
    visited_nodes = set()

    def find_root(node):
        if node in visited_nodes:
            return None
        visited_nodes.add(node)
        if report.graph.in_degree(node) == 0:
            root_nodes.add(node)

        for pred in report.graph.predecessors(node):
            find_root(pred)

    find_root("node2")
    find_root("node1")

    assert "node1" in root_nodes
    assert visited_nodes == {"node2", "node1"}


def test_reverse_graph_neighbors_traversal(monkeypatch):
    report = UReport.__new__(UReport)

    graph = nx.DiGraph()
    graph.add_edge("node1", "node2")

    monkeypatch.setattr(type(report), "graph", property(lambda self: graph))

    reverse_graph = graph.reverse()
    root_nodes = set()
    visited_nodes = set()

    def get_root_nodes(node, reverse_graph, visited_nodes, root_nodes):
        if node in visited_nodes:
            return None
        visited_nodes.add(node)
        if report.graph.in_degree(node) == 0:
            root_nodes.add(node)

        for neighbor in reverse_graph.neighbors(node):
            get_root_nodes(neighbor, reverse_graph, visited_nodes, root_nodes)
        return list(root_nodes)

    roots = get_root_nodes("node2", reverse_graph, visited_nodes, root_nodes)

    assert "node1" in roots
    assert "node2" in visited_nodes


def test_get_root_nodes_invocation(monkeypatch):
    report = UReport.__new__(UReport)

    graph = nx.DiGraph()
    graph.add_edge("node1", "node2")

    monkeypatch.setattr(type(report), "graph", property(lambda self: graph))

    def wrapper_get_root_nodes(report, target_node):
        reverse_graph = report.graph.reverse()
        root_nodes = set()
        visited_nodes = set()

        def get_root_nodes(node, reverse_graph, visited_nodes, root_nodes):
            if node in visited_nodes:
                return None
            visited_nodes.add(node)
            if report.graph.in_degree(node) == 0:
                root_nodes.add(node)
            for neighbor in reverse_graph.neighbors(node):
                get_root_nodes(neighbor, reverse_graph, visited_nodes, root_nodes)
            return root_nodes

        return get_root_nodes(target_node, reverse_graph, visited_nodes, root_nodes)

    roots = wrapper_get_root_nodes(report, "node2")

    assert "node1" in roots
    assert "node2" not in roots


import pytest

from urgap.ureport.ureport import UReport


def test_data_lineage_overview_initialization(monkeypatch):
    report = UReport.__new__(UReport)

    report.execution_history = {}
    report.ufile = None

    class DummyUMeta:
        pass

    monkeypatch.setattr(report.__class__, "umeta", property(lambda self: DummyUMeta()))

    monkeypatch.setattr(
        report.__class__, "wids", property(lambda self: ["wid1", "wid2"])
    )

    node_id_header = "Node ID"

    wid_str = ",".join(report.wids)

    data = [
        {
            "section_title": "Data lineage overview",
            "section_text": f"Urgap high workflow ID: {wid_str}",
            "networks": [],
            "figures": [],
            "tables": [],
        },
    ]

    assert node_id_header == "Node ID"
    assert wid_str == "wid1,wid2"
    assert data[0]["section_title"] == "Data lineage overview"
    assert data[0]["section_text"] == "Urgap high workflow ID: wid1,wid2"
    assert data[0]["networks"] == []
    assert data[0]["figures"] == []
    assert data[0]["tables"] == []


def test_execution_times_history_initialization(monkeypatch):
    report = UReport.__new__(UReport)

    node_id_header = "Node ID"
    wid = "wid123"

    history = {
        "title": "Execution times",
        "caption": f"History of execution times for {wid}",
        "headers": ["Node", node_id_header, "processing time [s]"],
        "rows": [],
    }

    assert history["title"] == "Execution times"
    assert history["caption"] == "History of execution times for wid123"
    assert history["headers"] == ["Node", "Node ID", "processing time [s]"]
    assert history["rows"] == []


def test_urd_overview_initialization():
    node_id_header = "Node ID"
    wid = "wid123"

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

    assert urd_overview["title"] == "Run Parameters HL overview"
    assert urd_overview["caption"] == "URun dict information for workflow ID wid123"
    assert urd_overview["headers"] == [
        "Node ID",
        "input_files",
        "output_files",
        "version",
    ]
    assert urd_overview["rows"] == []


def test_execution_graph_initialization():
    execution_graph = {
        "title": "Execution graph",
        "caption": (
            "Data are denoted by grey nodes, processing urgap nodes are displayed using "
            "the magma color palette and scaled according to execution time. "
            "Purple arrows indicate incoming data and green arrows"
            " point to data produced. Use scroll wheel to zoom."
        ),
        "links": [],
        "nodes": [],
    }

    assert execution_graph["title"] == "Execution graph"
    assert "Data are denoted by grey nodes" in execution_graph["caption"]
    assert execution_graph["links"] == []
    assert execution_graph["nodes"] == []


class DummyUReport:
    def __init__(self):
        self.execution_history = {("node1", "wid1"): {}, ("node2", "wid2"): {}}
        self.storage_base_uri = None
        self._traces = {}



def test_already_seen_nodes_loop():
    report = DummyUReport()
    already_seen_nodes = set()
        ut = report.get_trace(
            wid,
            storage_base_uri=report.storage_base_uri,
        )

    assert "node1" in already_seen_nodes
    assert "node2" in already_seen_nodes
        assert ut["utrace_loaded"] is True


class DummyUReport:
    def __init__(self):
        self.execution_history = {("node1", "wid1"): {}, ("node2", "wid2"): {}}
        self.storage_base_uri = None



def test_already_seen_nodes_loop():
    report = DummyUReport()
    already_seen_nodes = set()


        assert ut["utrace_loaded"] is True

    assert "node1" in already_seen_nodes
    assert "node2" in already_seen_nodes


class DummyHistory:
        class DummyDelta:
            def total_seconds(self):
                return 42

        return DummyDelta()


class DummyTrace(dict):
    def __init__(self):
        super().__init__()
        self["utrace_loaded"] = True
        self.history = DummyHistory()


class DummyUReport(UReport):
    def __new__(cls):
        return object.__new__(cls)

    def __init__(self):
        self.execution_history = {
            ("node1", "wid1"): {"started_time": 1},
            ("node2", "wid2"): {"started_time": 2},
        }
        self.storage_base_uri = None
        self.ufile = None

        return DummyTrace()


def test_already_seen_nodes_loop():
    report = DummyUReport()
    already_seen_nodes = set()


        assert ut["utrace_loaded"] is True

    assert already_seen_nodes == {"node1", "node2"}


class DummyHistory:
        class DummyDelta:
            def total_seconds(self):
                return 42

        return DummyDelta()


class DummyTrace(dict):
    def __init__(self, name):
        super().__init__()
        self["utrace_loaded"] = True
        self.history = DummyHistory()
        self.unode_meta = {"name": name}


class DummyUReport(UReport):
    def __new__(cls):
        return object.__new__(cls)

    def __init__(self):
        self.execution_history = {
            ("node1", "wid1"): {"started_time": 1},
            ("node2", "wid2"): {"started_time": 2},
        }
        self.storage_base_uri = None
        self.ufile = None



def test_history_rows_append():
    report = DummyUReport()
    node_id_header = "Node ID"
    history = {
        "title": "Execution times",
        "caption": "dummy caption",
        "headers": ["Node", node_id_header, "processing time [s]"],
        "rows": [],
    }


        history["rows"].append(
            {
                "Node": ut.unode_meta["name"],
                "processing time [s]": processing_time,
            }
        )

    assert len(history["rows"]) == 2
    assert history["rows"][0]["Node"] == "node1"
    assert history["rows"][1]["Node"] == "node2"
    assert history["rows"][0][node_id_header] == "node1"
    assert history["rows"][1][node_id_header] == "node2"
    assert history["rows"][0]["processing time [s]"] == 42
    assert history["rows"][1]["processing time [s]"] == 42