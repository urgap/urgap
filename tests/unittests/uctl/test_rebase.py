import json

from pathlib import Path
from types import SimpleNamespace

import pytest

from click.testing import CliRunner

import urgap

from urgap.uctl.rebase import (
    REBASE_SUBSCRIPTION_KEY,
    SourceNotFoundError,
    find_missing_sources,
    process_rebase_message,
    rebase_uris,
    rebase_uris_click,
)
from urgap.umessagebus.worker import UnprocessableMessageError

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


def get_missing_source_uri() -> str:
    return f"file://{urgap._test_folder}/data?uftype=.any.csv#unified_csvs/not_there.csv"


def test_rebase_uris_raises_for_missing_source_and_rebases_nothing(tmp_dir):
    missing_uri = get_missing_source_uri()
    with pytest.raises(SourceNotFoundError) as excinfo:
        rebase_uris(
            uris=[*get_source_uris(), missing_uri],
            storage_base_uri=f"file://{tmp_dir}",
        )
    assert [uri.split("#")[-1] for uri in excinfo.value.uris] == [
        "unified_csvs/not_there.csv",
    ]
    # the sources that do exist were not copied either
    assert not any(Path(tmp_dir).rglob("*.csv"))


def test_process_rebase_message_marks_missing_source_unprocessable(tmp_dir):
    with pytest.raises(UnprocessableMessageError, match="not_there.csv"):
        process_rebase_message(
            {
                "subscription_key": REBASE_SUBSCRIPTION_KEY,
                "consumer_kwargs": {
                    "input_uris": [get_missing_source_uri()],
                    "storage_base_uri": f"file://{tmp_dir}",
                },
            },
        )


def test_find_missing_sources_only_trusts_checked_backends():
    def must_not_be_called():
        msg = "remote_object_exists must not be called for this backend"
        raise AssertionError(msg)

    unchecked = SimpleNamespace(
        io=SimpleNamespace(SCHEMA="https", remote_object_exists=must_not_be_called),
        as_uri=lambda: "https://example.org#a.csv",
    )
    missing = SimpleNamespace(
        io=SimpleNamespace(SCHEMA="gcs", remote_object_exists=lambda: False),
        as_uri=lambda: "gcs://bucket#gone.csv",
    )
    present = SimpleNamespace(
        io=SimpleNamespace(SCHEMA="az-dl", remote_object_exists=lambda: True),
        as_uri=lambda: "az-dl://account/fs#there.csv",
    )
    assert find_missing_sources([unchecked, missing, present]) == [
        "gcs://bucket#gone.csv",
    ]
