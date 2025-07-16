
import urgap

from urgap.uctl.run import (
    dashboard_object_name_click,
    dashboard_uri_click,
    get_all_relevant_nodes,
)

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
    ufl = run_unode_in_loop(
        {
            "config": urgap.config,
        },
        "BasicFunctionTestNode:1.3.0",
    )
    assert len(ufl) == 1