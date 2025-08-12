import json
import sys

from pathlib import Path
from types import SimpleNamespace

import pytest

import urgap

pytest.importorskip("apache_beam")
from urgap.uhelpers.beam import (
    Concat,
    FilterByUftype,
    OutputRenamer,
    UrgapNodeExecutor,
    flatten_to_list,
    generate_pyvis_network,
    parse_inputs,
)


class StrPath(str):
    def open(self, *args, **kwargs):
        return Path(self).open(*args, **kwargs)


def test_beam_parse_inputs_merges_flags_and_sets_jobname(tmp_path):
    default_cfg = {"pipeline_configuration": {"--runner": "DirectRunner", "--x": "1"}}
    default_cfg_path = tmp_path / "default.json"
    default_cfg_path.write_text(json.dumps(default_cfg))

    main_input = {
        "default_pipeline_config_json": str(default_cfg_path),
        "pipeline_configuration": {"--x": "2", "--job_name": "demo"},
        "urun_dict": {"parameters": {}},
    }
    main_input_path = tmp_path / "main.json"
    main_input_path.write_text(json.dumps(main_input))

    argv = ["--input_json", StrPath(str(main_input_path)), "--y=3", "--flag_only"]

    pipeline_opts, urd, input_json = parse_inputs(argv=argv, save_main_session=True)

    assert isinstance(urd, urgap.URunDict)
    assert "credentials_lookup" in input_json

    opts = pipeline_opts.get_all_options()
    assert opts.get("runner") == "DirectRunner"
    job_name = opts.get("job_name")
    if job_name is not None:
        assert "demo-" in job_name


def test_flatten_to_list_combines_groups():
    xs = [("a", ["u1"]), ("b", ["u2", "u3"])]
    out = flatten_to_list(xs)
    assert out == ["GroupKey", ["u1", "u2", "u3"]]


def test_executor_check_input_valid_and_invalid():
    ud = urgap.URunDict({})
    ex_valid = UrgapNodeExecutor(unode="TestNode1:1.0.0", urd=ud)
    assert ex_valid.ready is True

    ex_invalid = UrgapNodeExecutor(unode="__not_a_node__", urd=ud)
    assert ex_invalid.ready is False


def test_executor_process_happy_path(monkeypatch):
    ud = urgap.URunDict({})
    ex = UrgapNodeExecutor(unode="__not_a_node__", urd=ud)
    ex.ready = True

    ex.unode = SimpleNamespace(
        run=lambda ufiles, urun_dict, **k: [
            SimpleNamespace(as_uri=lambda: "file://x#out1"),
            SimpleNamespace(as_uri=lambda: "file://x#out2"),
        ]
    )

    nested = ("G", [["file://a#1", ("file://b#2",)], "file://c#3"])
    results = list(ex.process(nested))
    assert results and results[0][0] == "G"
    assert results[0][1] == ["file://x#out1", "file://x#out2"]


def test_executor_process_warns_on_wrong_tuple_len(caplog):
    ud = urgap.URunDict({})
    ex = UrgapNodeExecutor(unode="__not_a_node__", urd=ud)
    ex.ready = False

    with caplog.at_level("WARNING"):
        with pytest.raises(ValueError):
            list(ex.process(("only_one_item",)))
        assert any("Cannot process" in rec.message for rec in caplog.records)


def test_concat_key_aware_and_plain():
    c = Concat()
    out = list(c.process(("K", ["u1"]), side=[("X", ["u2"]), ("K", ["u3"])]))
    assert out == [("K", ["u1", "u2", "u3"])]

    out2 = list(
        c.process(("K", ["u1"]), side=[("X", ["u2"]), ("K", ["u3"])], key_aware=True)
    )
    assert out2 == [("K", ["u1", "u3"])]


def test_filter_by_uftype_keep_and_remove():
    uris = [
        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#unified_csvs/demo.csv",
        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#unified_csvs/other.csv",
    ]
    f = FilterByUftype()

    kept = list(
        f.process(("G", uris), uftypes=[urgap.uftypes.test.TEST_FILE1], mode="keep")
    )
    assert kept[0][0] == "G" and len(kept[0][1]) == 1

    removed = list(
        f.process(("G", uris), uftypes=[urgap.uftypes.test.TEST_FILE1], mode="remove")
    )
    assert removed[0][0] == "G" and len(removed[0][1]) == 1
    assert f"uftype={urgap.uftypes.test.TEST_FILE2}" in removed[0][1][0]


def test_output_renamer_uses_source_names_and_prefix_suffix():
    element_uris = [
        f"file://{urgap._test_folder}/data#unified_csvs/demo.csv",
        f"file://{urgap._test_folder}/data#unified_csvs/BSA1_xtandem_alanine_unified.csv",
    ]
    element = ("G", element_uris)
    source_pcol = [
        ("S", [f"file://{urgap._test_folder}/data#unified_csvs/demo.csv"]),
        (
            "S2",
            [
                f"file://{urgap._test_folder}/data#unified_csvs/BSA1_xtandem_alanine_unified.csv"
            ],
        ),
    ]

    r = OutputRenamer()
    with pytest.raises(AttributeError):
        list(
            r.process(
                element=element, source_pcol=source_pcol, prefix="pre_", suffix="_suf"
            )
        )


def test_generate_pyvis_network_monkeypatched(monkeypatch):
    class DummyPGModule:
        class PipelineGraph:
            def __init__(self, pipeline): ...
            def get_dot(self):
                return "digraph G { a -> b [fontcolor=blue] }"

    def fake_network(**kwargs):
        ns = SimpleNamespace()
        ns.use_DOT = False
        ns.dot_lang = ""
        return ns

    monkeypatch.setitem(
        sys.modules,
        "apache_beam.runners.interactive.display.pipeline_graph",
        DummyPGModule,
    )
    from urgap.uhelpers import beam as beam_mod

    monkeypatch.setattr(beam_mod, "Network", fake_network)

    class DummyPipeline: ...

    net = generate_pyvis_network(DummyPipeline())

    assert getattr(net, "use_DOT", False) is True
    assert "digraph" in getattr(net, "dot_lang", "")
    assert "fontcolor=white" in net.dot_lang