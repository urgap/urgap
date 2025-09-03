import logging
import types

import pytest

import urgap

from urgap.uctl.mcp.tools import (
    calculate_nana,
    generate_workflow_id,
    list_container_times,
    mylabdata_urgap_storage_pattern,
    register_tools,
)


class DummyServer:
    def __init__(self):
        self.added = []

    def add_tool(self, func, name, desc):
        self.added.append((name, func, desc))


def test_storage_pattern_helpers():
    assert (
        mylabdata_urgap_storage_pattern("354557", "24-1-C4")
        == "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-1-C4"
    )


def test_calculate_nana():
    assert calculate_nana(weight=80, height=2.0) == 20.0


def test_generate_workflow_id_monkeypatched(monkeypatch):
    monkeypatch.setattr(
        urgap,
        "uwid_obj",
        types.SimpleNamespace(generate_wid=lambda: "u_red-fox-jumps-lazy-dog"),
    )
    assert generate_workflow_id() == "u_red-fox-jumps-lazy-dog"


def test_list_container_times_calls_ufile(monkeypatch):
    calls = {}

    class DummyUfile:
        def __init__(self, uri):
            calls["uri"] = uri

            calls["pattern"] = pattern
            calls["limit"] = limit
            calls["full_string"] = full_string
            return ["file://x#one", "file://x#two"]

    monkeypatch.setattr(urgap, "UFile", DummyUfile)

    assert out == ["file://x#one", "file://x#two"]
    assert calls["uri"].endswith("#dummy.txt")
    assert calls["pattern"] == r".*\.csv$"
    assert calls["limit"] == 10


def test_register_tools_registers_builtins(monkeypatch):
    monkeypatch.setattr(
        urgap.instances,
        "ufile_io_manager",
        types.SimpleNamespace(available_io_classes=["file", "https"]),
    )
    server = DummyServer()
    register_tools(server, nodes_list=[])
    names = {n for (n, _, _) in server.added}
    assert {
        "list_container_times",
        "generate_workflow_id",
        "mylabdata_urgap_storage_pattern",
    } <= names


def test_register_tools_adds_unode_tool_and_skips_when_missing_examples(
    monkeypatch, caplog
):
    class OkUNode:
        META_INFO = {
            "parameter_examples": {"x": 1},
            "input_uftypes": {"any.ANY": {"min": 0, "max": -1}},
        }

        def run_node_as_mcp_tool(self, **kwargs):
            """docstring"""

    class BadUNode:
        META_INFO = {}

    def dummy_init_unode(name):
        if name == "Good:1.0.0":
            return OkUNode()
        if name == "Bad:1.0.0":
            return BadUNode()
        raise AssertionError("unexpected")

    monkeypatch.setattr(urgap, "init_unode", dummy_init_unode)

    monkeypatch.setattr(
        urgap.instances,
        "ufile_io_manager",
        types.SimpleNamespace(available_io_classes=["file"]),
    )

    server = DummyServer()
    with caplog.at_level(logging.WARNING):
        register_tools(server, nodes_list=["Good:1.0.0", "Bad:1.0.0", "Foo:latest"])
    names = [n for (n, _, _) in server.added]
    assert "Good_1_0_0" in names
    assert any("parameter_example" in r.message for r in caplog.records)
    assert not any(n.startswith("Foo") for n in names)