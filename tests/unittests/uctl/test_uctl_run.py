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
