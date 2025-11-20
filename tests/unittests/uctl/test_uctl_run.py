import logging
import signal

from unittest.mock import patch

from click.testing import CliRunner
from fastapi.testclient import TestClient

import urgap

from urgap.uctl import run as run_module
from urgap.uctl.run import (
    create_app,
    dashboard_object_name_click,
    dashboard_uri_click,
    get_all_relevant_nodes,
    run_unode_in_loop,
    send_signal_to_pid,
)
from urgap.umeta.io.gcpsql import UMeta

runner = CliRunner()


def test_homepage():
    run_module.app.config["data"] = ["foo"]
    with run_module.app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"dashboard" in resp.data


def test_run_cli_group_loads():
    result = runner.invoke(run_module.run, ["--help"])
    assert result.exit_code == 0
    assert "Run Urgap services or jobs." in result.output


def test_create_app_and_livez_readyz():
    app = create_app("test_node")
    client = TestClient(app)
    resp = client.get("/livez")
    assert resp.status_code == 200
    assert resp.json() == {"status": "livez"}
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "readyz"}


def test_dashboard_uri_click(caplog):
    runner.invoke(
        dashboard_uri_click,
        [f"file://{urgap._test_folder}/data/unified_csvs#demo.csv"],
    )
    assert "<networkx.classes.digraph.DiGraph object at" in caplog.text
    assert "<urgap.umeta.umeta.UMeta object at" in caplog.text


def test_dashboard_object_name_click(caplog):
    runner.invoke(dashboard_object_name_click, ["test_wid"])
    assert "<networkx.classes.digraph.DiGraph object at" in caplog.text
    assert "<urgap.umeta.umeta.UMeta object at" in caplog.text


def test_get_all_relevant_nodes():
    to_spawn = get_all_relevant_nodes("BasicFunctionTestNode:latest")
    assert len(to_spawn) == 2
    assert to_spawn == ["BasicFunctionTestNode:latest", "BasicFunctionTestNode:1.3.0"]

    to_spawn = get_all_relevant_nodes("BasicFunctionTestNode:1.3.0")
    assert len(to_spawn) == 2
    assert to_spawn == ["BasicFunctionTestNode:1.3.0", "BasicFunctionTestNode:latest"]

    to_spawn = get_all_relevant_nodes("BasicFunctionTestNode:1.1.0")
    assert len(to_spawn) == 1
    assert to_spawn == ["BasicFunctionTestNode:1.1.0"]


def test_run_unode_in_loop(tmp_dir):
    from urgap.uctl.run import run_unode_in_loop

    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#test_node_data/test.txt",
            ),
        ],
    )
    # Filter out None credentials
    ucredentials = [
        cred
        for cred in urgap.instances.ucredential_manager.ingested_credentials.values()
        if cred is not None
    ]

    urun_dict = {
        "parameters": {
            "BasicFunctionTestNode:1.3.0": {
                "triggers_nuttin": 100,
                "triggers_rerun": 100,
                "no_rerun_node_trigger": 100,
            },
        },
        "unode_parameters": {
            "storage_base_uri": f"file://{tmp_dir}",
        },
    }
    ufl = run_unode_in_loop(
        {
            "ufiles": ufiles,
            "ucredentials": ucredentials,
            "config": urgap.config,
            "urun_dict": urun_dict,
        },
        "BasicFunctionTestNode:1.3.0",
    )
    assert len(ufl) == 1


def test_umeta_generate_connection_string(monkeypatch):
    # Patch the config dict key
    monkeypatch.setitem(
        urgap.config, "umeta-gcpsql-url", "postgresql+pg8000://host:5432"
    )

    # Patch extract_credentials
    monkeypatch.setattr(
        "urgap.instances.ucredential_manager.extract_credentials",
        lambda conn_str: {"user": "testuser", "password": "testpass"},
    )

    umeta = UMeta()  # <-- use gcpsql UMeta
    conn_string = umeta.generate_connection_string()
    expected = "postgresql+pg8000://testuser:testpass@host:5432/urgap"
    assert conn_string == expected


@patch("urgap.uctl.run.os.getpgrp")
@patch("urgap.uctl.run.os.killpg")
def test_send_signal_to_pid_success(mock_os_killpg, mock_os_getpgrp):
    """Test that send_signal_to_pid sends the correct signal to the process group."""
    mock_os_getpgrp.return_value = 12345

    send_signal_to_pid(signal.SIGINT)

    mock_os_killpg.assert_called_once_with(12345, signal.SIGINT)
    mock_os_getpgrp.assert_called_once()


@patch("urgap.uctl.run.os.getpgrp")
@patch("urgap.uctl.run.os.killpg")
def test_send_signal_to_pid_with_sigterm(mock_os_killpg, mock_os_getpgrp):
    """Test that send_signal_to_pid can send different signals."""
    mock_os_getpgrp.return_value = 54321

    send_signal_to_pid(signal.SIGTERM)

    mock_os_killpg.assert_called_once_with(54321, signal.SIGTERM)


@patch("urgap.uctl.run.os.getppid")
@patch("urgap.uctl.run.os.kill")
@patch("urgap.uctl.run.os.getpgrp")
@patch("urgap.uctl.run.os.killpg")
def test_send_signal_to_pid_handles_oserror_with_fallback(
    mock_os_killpg, mock_os_getpgrp, mock_os_kill, mock_os_getpid, caplog
):
    """Test that send_signal_to_pid falls back to current process on OSError."""
    mock_os_getpgrp.return_value = 12345
    mock_os_killpg.side_effect = OSError("Process group not found")
    mock_os_getpid.return_value = 67890

    with caplog.at_level(logging.WARNING):
        send_signal_to_pid(signal.SIGINT)

    mock_os_killpg.assert_called_once_with(12345, signal.SIGINT)
    mock_os_kill.assert_called_once_with(67890, signal.SIGINT)
    assert "Failed to send signal to process group 12345" in caplog.text


@patch("urgap.uctl.run.os.getpgrp")
@patch("urgap.uctl.run.os.killpg")
def test_send_signal_to_pid_default_signal(mock_os_killpg, mock_os_getpgrp):
    """Test that send_signal_to_pid uses SIGINT as default signal."""
    mock_os_getpgrp.return_value = 99999

    send_signal_to_pid()

    mock_os_killpg.assert_called_once_with(99999, signal.SIGINT)


@patch("urgap.uctl.run.os.getppid")
@patch("urgap.uctl.run.os.kill")
@patch("urgap.uctl.run.os.getpgrp")
@patch("urgap.uctl.run.os.killpg")
def test_send_signal_to_pid_both_fail(
    mock_os_killpg, mock_os_getpgrp, mock_os_kill, mock_os_getpid, caplog
):
    """Test that send_signal_to_pid handles both process group and fallback failures."""
    mock_os_getpgrp.return_value = 12345
    mock_os_killpg.side_effect = OSError("Process group not found")
    mock_os_getpid.return_value = 67890
    mock_os_kill.side_effect = OSError("Process not found")

    with caplog.at_level(logging.WARNING):
        send_signal_to_pid(signal.SIGINT)

    mock_os_killpg.assert_called_once_with(12345, signal.SIGINT)
    mock_os_kill.assert_called_once_with(67890, signal.SIGINT)
    assert "Failed to send signal to process group" in caplog.text
    assert "Failed to send signal to current process" in caplog.text