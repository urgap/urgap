"""Run submodule of urgap.uctl."""

import asyncio
import json
import logging
import multiprocessing
import os
import pprint
import signal
import threading
import traceback
import webbrowser

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from types import FrameType

import click
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from mcp.server.fastmcp import FastMCP

import urgap

from urgap.util import sort_versions

"""UPI server submodule of urgap.uctl.

This module provides utilities to launch FastAPI-based microservices for urgap nodes
for remote execution via HTTP endpoints, using uvicorn.
"""


def run_unode_in_loop(payload: dict, name: str) -> list:
    """Run a Urgap node inside an event loop context.

    Args:
        payload: The JSON payload to configure the node execution.
        name: Name of the urgap node to be executed.

    Returns:
        List of UFile UUris for output files.
    """
    urgap_node = urgap.init_node(name)
    urgap.config.update(payload["config"])
    urgap.instances.ucredential_manager.add_credentials(payload["ucredentials"])
    ur = urgap.URunDict(payload["urun_dict"])
    uf = payload["ufiles"]
    ur["unode_parameters"]["remote_url"] = None
    try:
        output_files = urgap_node.run(
            urun_dict=ur,
            ufiles=uf,
        )
    except Exception as e:
        msg = f"During remote run execution the following error occurred: {e}"
        raise
    return [o.as_uri() for o in output_files]


def create_app(name: str) -> FastAPI:
    """Create FastAPI app with /v1/run and /v1/terminate endpoints.

    Args:
        name: urgap node name to be executed by this server.

    Returns:
        FastAPI application instance.
    """
    app = FastAPI(title=name)
    app.state.name = name

    @app.post("/v1/run")
    async def run_unode(request: Request) -> JSONResponse:
        """Run UNode endpoint. Expects JSON payload with run parameters."""
        payload = await request.json()
        payload = json.loads(
            payload,
            cls=urgap.uconvert.JSONDecoder,
        )
        loop = asyncio.get_running_loop()
        msg = f"Launching urgap node {name}"

        try:
            output_files = await loop.run_in_executor(
                app.state.executor,
                run_unode_in_loop,
                payload,
                app.state.name,
            )
            return JSONResponse(
                content=output_files,
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                content={"error": str(e), "traceback": traceback.format_exc()},
                status_code=500,
            )

    @app.post("/v1/terminate")
    def terminate_server() -> dict:
        """Trigger server shutdown after responding 200."""
        app.state.shutdown_event.set()
        return {"message": "Server shutdown initiated."}

    @app.get("/livez")
    async def livez() -> JSONResponse:
        """Liveness probe endpoint."""
        return JSONResponse(status_code=200, content={"status": "livez"})

    @app.get("/readyz")
    async def readyz() -> JSONResponse:
        """Readiness probe endpoint."""
        return JSONResponse(status_code=200, content={"status": "readyz"})

    return app


    """Run uvicorn server in a background thread and listen for shutdown event.

    Args:
        name: urgap node name to serve.
        port: Port number to serve on.
        shutdown_event: multiprocessing.Event used to trigger shutdown.
    """
    app = create_app(name)
    app.state.shutdown_event = shutdown_event
    app.state.executor = ProcessPoolExecutor()

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.start()

    shutdown_event.wait()

    server.should_exit = True
    thread.join()


def run_mcp_server(
    nodes: list,
    mcp_port: int,
    shutdown_event: multiprocessing.Event,
    google_adk_style: bool = True,
) -> None:
    """Expose urgap nodes as MCP Server tools.

    Args:
        nodes (list): List of ursgal nodes
        mcp_port (int): port for the mcp sse server
        shutdown_event (multiprocessing.Event): ...
        google_adk_style (bool, optional): If resources and prompts should not be exposed. Defaults to True.
    """
    name = f"urgap mcp server for {', '.join(nodes)}"
    server = FastMCP(name)

    from urgap.uctl.mcp.tools import register_tools

    register_tools(server, nodes)

    if google_adk_style is False:
        from urgap.uctl.mcp.prompts import register_prompts
        from urgap.uctl.mcp.resources import register_resources

        register_resources(server)
        register_prompts(server)

    config = uvicorn.Config(
        server.sse_app(),
        host="127.0.0.1",
        port=int(mcp_port),
        log_level="info",
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.start()

    shutdown_event.wait()

    server.should_exit = True
    thread.join()



def get_all_relevant_nodes(nodes: tuple | str) -> list:
    """Expand provided nodes to include both 'latest' and explicit version for each node.

    Args:
        nodes: Node names or versions to expand.

    Returns:
        List of nodes to serve, ensuring both 'latest' and its explicit version are included.
    """
    if isinstance(nodes, tuple):
        nodes_list = list(nodes)
    elif isinstance(nodes, str):
        nodes_list = [nodes]
    for unode in nodes_list:
        unode_name, _ = unode.split(":")
        all_unode_versions = [
            node.split(":")[1]
            for node in sorted(
                urgap.instances.unode_manager.wrapper_lookup.keys(),
                key=sort_versions,
            )
            if node.split(":")[0] == unode_name
        ]

        actual_latest_version = unode_name + ":" + all_unode_versions[-1]
        latest_in_name = unode_name + ":latest"

        if unode == latest_in_name and actual_latest_version not in nodes_list:
            nodes_list.append(actual_latest_version)
        elif unode == actual_latest_version and latest_in_name not in nodes_list:
            nodes_list.append(latest_in_name)
    return nodes_list


@click.command()
@click.option(
    "--nodes",
    "-n",
    help="Nodes for which to start server.",
    required=True,
    multiple=True,
)
@click.option(
    "--mcp",
    "-m",
    help="Expose Nodes as model context protocol tools given port.",
    required=False,
    multiple=False,
    default=None,
)

    """
    processes = []
    shutdown_event = multiprocessing.Event()
    nodes_list = get_all_relevant_nodes(nodes=nodes)
    for unode in nodes_list:
        port = urgap.instances.unode_manager.unode_port_mapping[unode]
        p = multiprocessing.Process(
            target=run_server,
            args=(
                unode,
                port,
                shutdown_event,
            ),
        )
        processes.append(p)
        p.start()

    if mcp is not None:
        p = multiprocessing.Process(
            target=run_mcp_server,
            args=(
                nodes_list,
                mcp,
                shutdown_event,
            ),
        )
        processes.append(p)
        p.start()

    def signal_handler(sig: int, _frame: FrameType | None) -> None:
        msg = f"Parent process received termination signal {sig}"
        for proc in processes:
            proc.terminate()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    for process in processes:
        process.join()


"""Dashboard submodule of urgap.uctl."""
urgap_server = Path(__file__).parent / "server"
urgap_server_static = urgap_server / "static"
urgap_server_templates = urgap_server / "templates"

app = Flask(
    __name__,
    static_folder=urgap_server_static,
    template_folder=urgap_server_templates,
)
csrf = CSRFProtect()
csrf.init_app(app)


@app.route("/")
def homepage() -> str:
    """Homepage of the dashboard.

    Returns the dashboard base info page.
    """
    with app.app_context():
        return render_template(
            "dashboard.html",
            version="0.7.0",
            data=app.config["data"],
        )


def launch_dashboard() -> None:
    """Launch the dashboard and open in a web browser."""
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new("http://127.0.0.1:2000/")
    app.run(host="127.0.0.1", port=2000)


@click.group()
def dashboard() -> None:
    """Spin up the urgap dashboard."""


@click.command()
@click.argument("wid")
def dashboard_wid_click(wid: str) -> None:
    """Show dashboard for a given workflow ID (wid)."""
    app.config["data"] = []
    ur = urgap.UReport(wid=wid)
    app.config["data"] = ur.generate_report()
    launch_dashboard()


@click.command()
@click.argument("uri")
def dashboard_uri_click(uri: str) -> None:
    """Show dashboard based on a file UUri.

    Note: Currently only works with mongo backend.
    """
    ufile = urgap.UFile(uri=uri)
    ur = urgap.UReport(ufile=ufile)
    logging.info(pprint.pformat(ur.graph))
    logging.info(pprint.pformat(ur))
    logging.info(
        pprint.pformat(
            "Dashboard for all wids might be the overkill. Please select one.",
        ),
    )


@click.command()
@click.argument("object_name")
def dashboard_object_name_click(object_name: str) -> None:
    """Show dashboard based on object name.

    Note: Currently only works with mongo backend.
    """
    ur = urgap.UReport(ucfs=object_name)
    logging.info(pprint.pformat(ur.graph))
    logging.info(pprint.pformat(ur))
    logging.info(
        pprint.pformat(
            "Dashboard for all wids might be the overkill. Please select one.",
        ),
    )


@click.group()
def run() -> None:
    """Run Urgap services or jobs."""


run.add_command(upi_server)
run.add_command(dashboard)