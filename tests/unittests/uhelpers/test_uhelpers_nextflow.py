"""Unit tests for urgap.uhelpers.nextflow.

Tests cover each helper function in isolation.  Functions that touch urgap
globals (``setup_urgap``) are tested against the live urgap instances so that
the behaviour matches the Prefect / Beam test patterns in this repo.
``run_unode`` patches ``urgap.init_unode`` to avoid running actual nodes.
"""

import json
import tempfile

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import urgap

from urgap.uhelpers.nextflow import (
    INCOMPLETE_WARNING,
    parse_cli_args,
    parse_config,
    read_uri_file,
    read_uri_files,
    run_unode,
    setup_urgap,
    write_uri_file,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_URIS = [
    f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
    "#unified_csvs/BSA1_xtandem_alanine_unified.csv",
    f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
    "#unified_csvs/demo.csv",
]

CREDS = [
    {
        "host": "thats_a_host",
        "user": "a_user",
        "scheme": "a_scheme",
        "secure": True,
        "password": "much_safe_very_secure",
        "description": "test credential",
        "secret_store": "env",
    }
]

CONFIG_OVERRIDE = {"i_hope": "this_gets_added"}

MINIMAL_CONFIG_DICT = {
    "urun_dict": {
        "parameters": {"TestNode1:1.0.0": {}},
        "unode_parameters": {"storage_base_uri": "file:///tmp/test_output"},
    },
    "credentials_lookup": CREDS,
    "config": CONFIG_OVERRIDE,
}


# ---------------------------------------------------------------------------
# read_uri_file
# ---------------------------------------------------------------------------


def test_read_uri_file_returns_uris(tmp_path):
    """Basic read: all non-blank, non-comment lines are returned."""
    uri_file = tmp_path / "uris.txt"
    uri_file.write_text("\n".join(SAMPLE_URIS) + "\n")

    result = read_uri_file(uri_file)

    assert result == SAMPLE_URIS


def test_read_uri_file_skips_blank_lines(tmp_path):
    """Blank lines interspersed with URIs are silently ignored."""
    uri_file = tmp_path / "uris.txt"
    uri_file.write_text(f"\n{SAMPLE_URIS[0]}\n\n{SAMPLE_URIS[1]}\n\n")

    result = read_uri_file(uri_file)

    assert result == SAMPLE_URIS


def test_read_uri_file_skips_comment_lines(tmp_path):
    """Lines starting with '#' are treated as comments and skipped."""
    uri_file = tmp_path / "uris.txt"
    uri_file.write_text(f"# this is a comment\n{SAMPLE_URIS[0]}\n# another comment\n")

    result = read_uri_file(uri_file)

    assert result == [SAMPLE_URIS[0]]


def test_read_uri_file_empty_file_returns_empty_list(tmp_path):
    """An empty (or whitespace-only) file returns an empty list."""
    uri_file = tmp_path / "uris.txt"
    uri_file.write_text("  \n  \n")

    result = read_uri_file(uri_file)

    assert result == []


def test_read_uri_file_accepts_string_path(tmp_path):
    """Path may be passed as a plain string, not just a Path object."""
    uri_file = tmp_path / "uris.txt"
    uri_file.write_text(SAMPLE_URIS[0] + "\n")

    result = read_uri_file(str(uri_file))

    assert result == [SAMPLE_URIS[0]]


def test_read_uri_file_raises_for_missing_file(tmp_path):
    """FileNotFoundError is raised when the file does not exist."""
    with pytest.raises(FileNotFoundError):
        read_uri_file(tmp_path / "does_not_exist.txt")


# ---------------------------------------------------------------------------
# read_uri_files
# ---------------------------------------------------------------------------


def test_read_uri_files_single_file(tmp_path):
    """Single-file case behaves identically to read_uri_file."""
    uri_file = tmp_path / "uris.txt"
    uri_file.write_text("\n".join(SAMPLE_URIS) + "\n")

    result = read_uri_files([uri_file])

    assert result == SAMPLE_URIS


def test_read_uri_files_merges_multiple_files(tmp_path):
    """URIs from all files are merged in file order."""
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_c = tmp_path / "c.txt"

    file_a.write_text(SAMPLE_URIS[0] + "\n")
    file_b.write_text(SAMPLE_URIS[1] + "\n")
    extra_uri = "file:///extra?uftype=x#extra.csv"
    file_c.write_text(extra_uri + "\n")

    result = read_uri_files([file_a, file_b, file_c])

    assert result == [SAMPLE_URIS[0], SAMPLE_URIS[1], extra_uri]


def test_read_uri_files_deduplicates_across_files(tmp_path):
    """Duplicate URIs appearing in multiple files are included only once."""
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"

    file_a.write_text(SAMPLE_URIS[0] + "\n")
    file_b.write_text(SAMPLE_URIS[0] + "\n")  # same URI repeated

    result = read_uri_files([file_a, file_b])

    assert result == [SAMPLE_URIS[0]]
    assert len(result) == 1


def test_read_uri_files_preserves_order(tmp_path):
    """First-seen order is preserved during deduplication."""
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"

    file_a.write_text(SAMPLE_URIS[0] + "\n" + SAMPLE_URIS[1] + "\n")
    file_b.write_text(SAMPLE_URIS[1] + "\n" + SAMPLE_URIS[0] + "\n")

    result = read_uri_files([file_a, file_b])

    assert result == SAMPLE_URIS  # order from file_a wins


def test_read_uri_files_raises_for_empty_paths_list():
    """ValueError is raised when no paths are provided."""
    with pytest.raises(ValueError):
        read_uri_files([])


# ---------------------------------------------------------------------------
# write_uri_file
# ---------------------------------------------------------------------------


def test_write_uri_file_writes_uris(tmp_path):
    """Each URI appears on its own line in the output file."""
    out = tmp_path / "output_uris.txt"

    write_uri_file(SAMPLE_URIS, out)

    lines = out.read_text().splitlines()
    assert lines == SAMPLE_URIS


def test_write_uri_file_skips_none_values(tmp_path):
    """None entries are silently omitted from the output."""
    out = tmp_path / "output_uris.txt"
    uris_with_none = [SAMPLE_URIS[0], None, SAMPLE_URIS[1]]

    write_uri_file(uris_with_none, out)

    lines = out.read_text().splitlines()
    assert lines == SAMPLE_URIS


def test_write_uri_file_empty_list_creates_empty_file(tmp_path):
    """An empty URI list produces a zero-byte (or newline-only) file."""
    out = tmp_path / "empty.txt"

    write_uri_file([], out)

    assert out.exists()
    assert out.read_text().strip() == ""


def test_write_uri_file_accepts_string_path(tmp_path):
    """Path may be passed as a string."""
    out = tmp_path / "output_uris.txt"

    write_uri_file([SAMPLE_URIS[0]], str(out))

    assert out.read_text().strip() == SAMPLE_URIS[0]


def test_write_then_read_roundtrip(tmp_path):
    """URIs written by write_uri_file can be recovered by read_uri_file."""
    out = tmp_path / "roundtrip.txt"

    write_uri_file(SAMPLE_URIS, out)
    recovered = read_uri_file(out)

    assert recovered == SAMPLE_URIS


# ---------------------------------------------------------------------------
# parse_config
# ---------------------------------------------------------------------------


def test_parse_config_basic(tmp_path):
    """Minimal config JSON is parsed into (URunDict, list, dict)."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(MINIMAL_CONFIG_DICT))

    urd, creds, config = parse_config(config_file)

    assert isinstance(urd, urgap.URunDict)
    assert creds == CREDS
    assert config == CONFIG_OVERRIDE


def test_parse_config_missing_optional_keys(tmp_path):
    """Config without credentials or config overrides uses sensible defaults."""
    minimal = {"urun_dict": {"parameters": {}, "unode_parameters": {}}}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(minimal))

    urd, creds, config = parse_config(config_file)

    assert isinstance(urd, urgap.URunDict)
    assert creds == []
    assert config == {}


def test_parse_config_with_default_pipeline_config_json(tmp_path):
    """default_pipeline_config_json is loaded and merged under urun_dict."""
    default_conf = {"pipeline_configuration": {"default_param": "default_value"}}
    default_file = tmp_path / "default.json"
    default_file.write_text(json.dumps(default_conf))

    config_dict = {
        "urun_dict": {
            "parameters": {"MyNode:1.0.0": {}},
            "unode_parameters": {"storage_base_uri": "file:///tmp"},
        },
        "default_pipeline_config_json": str(default_file),
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_dict))

    urd, _, _ = parse_config(config_file)

    # The default values should be accessible in the resulting URunDict
    assert isinstance(urd, urgap.URunDict)


def test_parse_config_explicit_overrides_defaults(tmp_path):
    """Explicit urun_dict values take precedence over default_pipeline_config_json.

    Mirrors beam's test_beam_parse_inputs_merges_flags_and_sets_jobname which
    asserts that --x=2 (explicit) beats --x=1 (from default file).
    """
    default_conf = {
        "pipeline_configuration": {
            "storage_base_uri": "file:///default_location",
            "only_in_default": "should_appear",
        }
    }
    default_file = tmp_path / "default.json"
    default_file.write_text(json.dumps(default_conf))

    config_dict = {
        "urun_dict": {
            "parameters": {"MyNode:1.0.0": {}},
            "unode_parameters": {
                "storage_base_uri": "file:///explicit_location",  # overrides default
            },
        },
        "default_pipeline_config_json": str(default_file),
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_dict))

    urd, _, _ = parse_config(config_file)

    # The explicit storage_base_uri must win over the default
    assert urd.unode_parameters["storage_base_uri"] == "file:///explicit_location"


def test_parse_config_raises_for_missing_urun_dict(tmp_path):
    """KeyError is raised when 'urun_dict' key is absent."""
    config_file = tmp_path / "bad_config.json"
    config_file.write_text(json.dumps({"credentials_lookup": []}))

    with pytest.raises(KeyError):
        parse_config(config_file)


def test_parse_config_raises_for_missing_file(tmp_path):
    """FileNotFoundError is raised when the config file does not exist."""
    with pytest.raises(FileNotFoundError):
        parse_config(tmp_path / "nonexistent.json")


def test_parse_config_accepts_string_path(tmp_path):
    """config_path may be a plain string."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(MINIMAL_CONFIG_DICT))

    urd, _, _ = parse_config(str(config_file))

    assert isinstance(urd, urgap.URunDict)


# ---------------------------------------------------------------------------
# setup_urgap
# ---------------------------------------------------------------------------


def test_setup_urgap_updates_config():
    """setup_urgap applies config overrides to urgap.config."""
    setup_urgap(ucredentials=[], config={"logging_level": "DEBUG"})

    assert urgap.config.get("logging_level") == "DEBUG"


def test_setup_urgap_injects_credentials():
    """setup_urgap adds credentials to the global credential manager."""
    setup_urgap(ucredentials=CREDS, config={})

    assert (
        "a_scheme://thats_a_host"
        in urgap.instances.ucredential_manager.ingested_credentials
    )


def test_setup_urgap_empty_credentials_and_config():
    """setup_urgap is a no-op for empty inputs (does not raise)."""
    setup_urgap(ucredentials=[], config={})  # must not raise


# ---------------------------------------------------------------------------
# run_unode
# ---------------------------------------------------------------------------


def test_run_unode_returns_zero_on_success(tmp_path):
    """run_unode returns 0 when the node executes successfully."""
    uri_file = tmp_path / "input_uris.txt"
    uri_file.write_text(
        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
        "#unified_csvs/BSA1_xtandem_alanine_unified.csv\n"
    )
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {
                "parameters": {"TestNode1:1.0.0": {}},
                "unode_parameters": {"storage_base_uri": f"file://{tmp_path}"},
            },
            "credentials_lookup": [],
            "config": {},
        })
    )

    mock_node = MagicMock()
    mock_ufile = MagicMock()
    mock_ufile.as_uri.return_value = "file:///output#result.csv"
    mock_node.run.return_value = [mock_ufile]

    with patch("urgap.init_unode", return_value=mock_node):
        exit_code = run_unode(
            input_uri_files=[uri_file],
            output_uri_file=output_file,
            unode="TestNode1:1.0.0",
            config_path=config_file,
        )

    assert exit_code == 0
    assert output_file.exists()
    assert "file:///output#result.csv" in output_file.read_text()


def test_run_unode_logs_incomplete_warning_on_empty_input(tmp_path, caplog):
    """INCOMPLETE_WARNING is logged when the input URI file is empty.

    Mirrors beam's test_executor_process_warns_on_wrong_tuple_len which asserts
    the specific warning message appears in the log, not just the exit code.
    """
    uri_file = tmp_path / "input_uris.txt"
    uri_file.write_text("")
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {"parameters": {}, "unode_parameters": {}},
            "credentials_lookup": [],
            "config": {},
        })
    )

    with caplog.at_level("WARNING"):
        run_unode(
            input_uri_files=[uri_file],
            output_uri_file=output_file,
            unode="TestNode1:1.0.0",
            config_path=config_file,
        )

    assert any(
        INCOMPLETE_WARNING in record.message for record in caplog.records
    ), f"Expected '{INCOMPLETE_WARNING}' in log records, got: {[r.message for r in caplog.records]}"


def test_run_unode_invalid_node_name_returns_error(tmp_path):
    """run_unode returns exit code 1 when the node name is not registered.

    Mirrors beam's test_executor_check_input_valid_and_invalid which tests
    with '__not_a_node__' and asserts ready=False. In the nextflow helper the
    equivalent is an exit code 1 since there is no persistent ready flag.
    """
    uri_file = tmp_path / "input_uris.txt"
    uri_file.write_text(SAMPLE_URIS[0] + "\n")
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {
                "parameters": {"__not_a_node__:1.0.0": {}},
                "unode_parameters": {"storage_base_uri": f"file://{tmp_path}"},
            },
            "credentials_lookup": [],
            "config": {},
        })
    )

    exit_code = run_unode(
        input_uri_files=[uri_file],
        output_uri_file=output_file,
        unode="__not_a_node__:1.0.0",
        config_path=config_file,
    )

    assert exit_code == 1


def test_run_unode_with_real_node(tmp_path):
    """run_unode executes a real urgap node end-to-end (no mocks).

    Mirrors prefect's test_run_unode which calls run_unode.fn() with a real
    TestNode1:1.0.0 and asserts the output URIs are strings.
    """
    uri_file = tmp_path / "input_uris.txt"
    uri_file.write_text(
        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
        "#unified_csvs/BSA1_xtandem_alanine_unified.csv\n"
    )
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {
                "parameters": {"TestNode1:1.0.0": {}},
                "unode_parameters": {"storage_base_uri": f"file://{tmp_path}"},
            },
            "credentials_lookup": [],
            "config": {},
        })
    )

    exit_code = run_unode(
        input_uri_files=[uri_file],
        output_uri_file=output_file,
        unode="TestNode1:1.0.0",
        config_path=config_file,
    )

    assert exit_code == 0
    assert output_file.exists()
    output_uris = read_uri_file(output_file)
    assert len(output_uris) >= 1
    for uri in output_uris:
        assert isinstance(uri, str)
        assert "://" in uri  # valid URI format


def test_run_unode_returns_two_for_empty_input(tmp_path):
    """run_unode returns exit code 2 when the input URI file is empty."""
    uri_file = tmp_path / "input_uris.txt"
    uri_file.write_text("")  # empty
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {"parameters": {}, "unode_parameters": {"storage_base_uri": f"file://{tmp_path}"}},
            "credentials_lookup": [],
            "config": {},
        })
    )

    exit_code = run_unode(
        input_uri_files=[uri_file],
        output_uri_file=output_file,
        unode="TestNode1:1.0.0",
        config_path=config_file,
    )

    assert exit_code == 2
    assert output_file.exists()  # empty output file is still written


def test_run_unode_merges_multiple_input_files(tmp_path):
    """run_unode merges URIs from multiple input files before calling the node."""
    uri_file_a = tmp_path / "a.txt"
    uri_file_b = tmp_path / "b.txt"
    uri_file_a.write_text(SAMPLE_URIS[0] + "\n")
    uri_file_b.write_text(SAMPLE_URIS[1] + "\n")
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {
                "parameters": {"ConcatCSVs:1.0.0": {}},
                "unode_parameters": {"storage_base_uri": f"file://{tmp_path}"},
            },
            "credentials_lookup": [],
            "config": {},
        })
    )

    mock_node = MagicMock()
    mock_ufile = MagicMock()
    mock_ufile.as_uri.return_value = "file:///output#merged.csv"
    mock_node.run.return_value = [mock_ufile]

    with patch("urgap.init_unode", return_value=mock_node) as mock_init:
        run_unode(
            input_uri_files=[uri_file_a, uri_file_b],
            output_uri_file=output_file,
            unode="ConcatCSVs:1.0.0",
            config_path=config_file,
        )

    # node.run should have been called with both URIs merged
    call_kwargs = mock_node.run.call_args
    passed_uris = call_kwargs.kwargs.get("ufiles") or call_kwargs.args[0]
    # The merged list must contain both URIs
    assert any(SAMPLE_URIS[0] in str(u) for u in passed_uris)
    assert any(SAMPLE_URIS[1] in str(u) for u in passed_uris)


def test_run_unode_output_file_written_even_on_skip(tmp_path):
    """Output URI file is always written, even when urgap skips (PaC hit)."""
    uri_file = tmp_path / "input_uris.txt"
    uri_file.write_text(SAMPLE_URIS[0] + "\n")
    output_file = tmp_path / "output_uris.txt"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "urun_dict": {
                "parameters": {"TestNode1:1.0.0": {}},
                "unode_parameters": {"storage_base_uri": f"file://{tmp_path}"},
            },
            "credentials_lookup": [],
            "config": {},
        })
    )

    mock_node = MagicMock()
    # Simulate a PaC skip: node.run still returns output URIs (pre-existing outputs)
    mock_ufile = MagicMock()
    mock_ufile.as_uri.return_value = SAMPLE_URIS[0]
    mock_node.run.return_value = [mock_ufile]

    with patch("urgap.init_unode", return_value=mock_node):
        exit_code = run_unode(
            input_uri_files=[uri_file],
            output_uri_file=output_file,
            unode="TestNode1:1.0.0",
            config_path=config_file,
        )

    assert exit_code == 0
    assert output_file.exists()


# ---------------------------------------------------------------------------
# parse_cli_args
# ---------------------------------------------------------------------------


def test_parse_cli_args_minimal(tmp_path):
    """Required args are parsed correctly."""
    argv = [
        "--unode", "FilterTabularToCSV:1.0.0",
        "--input_uris", "input.txt",
        "--output_uris", "output.txt",
        "--config", "config.json",
    ]
    args = parse_cli_args(argv)

    assert args.unode == "FilterTabularToCSV:1.0.0"
    assert args.input_uris == ["input.txt"]
    assert args.output_uris == "output.txt"
    assert args.config == "config.json"
    assert args.log_level is None


def test_parse_cli_args_multiple_input_uris(tmp_path):
    """Multiple --input_uris values are collected into a list."""
    argv = [
        "--unode", "ConcatCSVs:1.0.0",
        "--input_uris", "a.txt", "b.txt", "c.txt",
        "--output_uris", "output.txt",
        "--config", "config.json",
    ]
    args = parse_cli_args(argv)

    assert args.input_uris == ["a.txt", "b.txt", "c.txt"]


def test_parse_cli_args_log_level(tmp_path):
    """Optional --log_level is parsed."""
    argv = [
        "--unode", "TestNode1:1.0.0",
        "--input_uris", "input.txt",
        "--output_uris", "output.txt",
        "--config", "config.json",
        "--log_level", "DEBUG",
    ]
    args = parse_cli_args(argv)

    assert args.log_level == "DEBUG"


def test_parse_cli_args_missing_required_raises():
    """SystemExit is raised when a required argument is missing."""
    with pytest.raises(SystemExit):
        parse_cli_args(["--unode", "TestNode1:1.0.0"])
