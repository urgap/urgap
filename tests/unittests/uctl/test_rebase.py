import json

from click.testing import CliRunner

import urgap

from urgap.uctl.rebase import (
    REBASE_SUBSCRIPTION_KEY,
    process_rebase_message,
    rebase_uris,
    rebase_uris_click,
)

runner = CliRunner()

SOURCE_OBJECT_NAMES = ["unified_csvs/demo.csv", "unified_csvs/human_ecoli_sample_pyiohat.csv"]


def get_source_uris() -> list[str]:
    return [
        f"file://{urgap._test_folder}/data?uftype=.any.csv#{object_name}"
        for object_name in SOURCE_OBJECT_NAMES
    ]


def test_rebase_uris_keeps_object_names(tmp_dir):
    resulting_uris = rebase_uris(
        uris=get_source_uris(),
        storage_base_uri=f"file://{tmp_dir}",
    )
    rebased = urgap.UFileList.from_uri_list(resulting_uris)
    assert [uf.object_name for uf in rebased] == SOURCE_OBJECT_NAMES
    assert all(uf.io.remote_object_exists() for uf in rebased)
    # the uftype survives so the files stay usable downstream
    assert {uf.uftype for uf in rebased} == {urgap.uftypes.any.CSV}


def test_rebase_uris_leaves_source_untouched(tmp_dir):
    source = urgap.UFileList.from_uri_list(get_source_uris())
    rebase_uris(uris=get_source_uris(), storage_base_uri=f"file://{tmp_dir}")
    assert all(uf.io.remote_object_exists() for uf in source)


def test_rebase_uris_content_matches_source(tmp_dir):
    source = urgap.UFileList.from_uri_list(get_source_uris())
    expected = {uf.object_name: uf.path.read_bytes() for uf in source}
    resulting_uris = rebase_uris(
        uris=get_source_uris(),
        storage_base_uri=f"file://{tmp_dir}",
    )
    for uf in urgap.UFileList.from_uri_list(resulting_uris):
        assert uf.path.read_bytes() == expected[uf.object_name]


def test_rebase_uris_click(tmp_dir, caplog):
    runner.invoke(
        rebase_uris_click,
        [f"file://{tmp_dir}", *get_source_uris()],
    )
    assert "Rebase finished, final uris:" in caplog.text
    for object_name in SOURCE_OBJECT_NAMES:
        assert object_name in caplog.text


def test_process_rebase_message(tmp_dir):
    ok, output_uris = process_rebase_message(
        {
            "uuid": "an-id",
            "subscription_key": REBASE_SUBSCRIPTION_KEY,
            "consumer_kwargs": {
                "input_uris": get_source_uris(),
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    assert ok is True
    rebased = urgap.UFileList.from_uri_list(output_uris)
    assert [uf.object_name for uf in rebased] == SOURCE_OBJECT_NAMES
    assert all(uf.io.remote_object_exists() for uf in rebased)


def test_process_rebase_message_applies_config(tmp_dir):
    ok, _output_uris = process_rebase_message(
        {
            "subscription_key": REBASE_SUBSCRIPTION_KEY,
            "consumer_kwargs": {
                "input_uris": get_source_uris(),
                "storage_base_uri": f"file://{tmp_dir}",
                "config": {"service_bus_topic": "topic_from_message"},
                "ucredentials": [],
            },
        },
    )
    assert ok is True
    assert urgap.config["service_bus_topic"] == "topic_from_message"


def test_process_rebase_message_reports_failure():
    ok, output_uris = process_rebase_message({"consumer_kwargs": {}})
    assert ok is False
    assert output_uris is None


def test_rebase_message_round_trip_is_json_serializable(tmp_dir):
    message = {
        "uuid": "an-id",
        "subscription_key": REBASE_SUBSCRIPTION_KEY,
        "consumer_kwargs": {
            "input_uris": get_source_uris(),
            "storage_base_uri": f"file://{tmp_dir}",
        },
    }
    ok, _output_uris = process_rebase_message(json.loads(json.dumps(message)))
    assert ok is True
