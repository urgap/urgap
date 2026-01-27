"""Run submodule of urgap.uctl."""

import asyncio
import json
import logging
import multiprocessing
import os
import pprint
import signal
import threading
import time
import traceback
import webbrowser

from concurrent.futures import ProcessPoolExecutor
from multiprocessing.synchronize import Event as EventClass
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

logger = logging.getLogger(__name__)

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
        logger.exception(msg)
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
        logger.info(msg)

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
            logger.exception("Error during remote UNode execution!")
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


def run_server(
    name: str,
    port: int,
    shutdown_event: EventClass,
) -> None:
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

    send_signal_to_pid()


def send_signal_to_pid(sig: int = signal.SIGINT) -> None:
    """Send the specified signal to the entire process group.

    This ensures that when running with multiple workers (e.g., uvicorn with --workers > 1),
    all worker processes receive the signal, not just the parent process.

    Args:
        sig: Signal to send (default: SIGINT for graceful shutdown)
    """
    try:
        pgid = os.getpgrp()
        os.killpg(pgid, sig)
        logger.info(
            "Sent signal %s to process group %s (includes all worker processes)",
            sig,
            pgid,
        )
    except OSError as e:
        logger.warning("Failed to send signal to process group %s: %s", pgid, e)
        try:
            pid = os.getppid()
            os.kill(pid, sig)
            logger.info(
                "Sent signal %s to current process %s (fallback)",
                sig,
                pid,
            )
        except OSError as e2:
            logger.warning("Failed to send signal to current process: %s", e2)


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

    send_signal_to_pid()


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


def _ensure_service_bus_entities(
    namespace: str,
    credential: object,
    topic_subscription_filter_pairs: list,
) -> None:
    from azure.core.exceptions import ResourceNotFoundError
    from azure.servicebus.management import (
        ServiceBusAdministrationClient,
        SqlRuleFilter,
    )

    admin = ServiceBusAdministrationClient(
        fully_qualified_namespace=namespace,
        credential=credential,
    )
    for (
        topic,
        subscription,
        filter_value,
    ) in topic_subscription_filter_pairs:  # renamed from filter (ruff A001)
        newly_created_subscription = False
        try:
            admin.get_topic(topic)
        except ResourceNotFoundError:
            admin.create_topic(topic_name=topic)
        try:
            admin.get_subscription(topic, subscription)
        except ResourceNotFoundError:
            admin.create_subscription(topic_name=topic, subscription_name=subscription)
            newly_created_subscription = True

        if (filter_value is not None) and newly_created_subscription:
            admin.delete_rule(topic, subscription, "$Default")
            admin.create_rule(
                topic_name=topic,
                subscription_name=subscription,
                rule_name="unode_filter",
                filter=SqlRuleFilter(
                    f"subscription_key = '{filter_value}'",
                ),
            )


def _publish_completion(
    sender: object,
    completion_topic: str | None,
    event: dict,
) -> None:
    """Publish a completion event.

    Args:
        sender: Service Bus sender object.
        completion_topic: Topic name if completion publishing enabled, else None.
        event: Event payload dictionary to serialize.
    """
    if not completion_topic:
        return
    from azure.servicebus import ServiceBusMessage

    app_props = {"subscription_key": event.get("subscription_key")}
    sender.send_messages(
        ServiceBusMessage(
            json.dumps(event),
            application_properties=app_props,
            correlation_id=event.get("uuid"),
        ),
    )


def _process_message(
    body: object,
) -> tuple[bool, list[str] | None]:
    """Process a Service Bus message using the strict minimal schema.

    Required schema keys (all mandatory):
      - uuid
      - wid
      - unode_full_identifier
      - urun_dict
      - input_uris
      - config
      - ucredentials

    Returns (ok, output_uris).
    On failure ok=False and output_uris=None.
    """
    ok = False
    output_uris = None
    try:
        consumer_kwargs = body["consumer_kwargs"]
        urgap.config.update(consumer_kwargs["config"])
        urgap.instances.ucredential_manager.add_credentials(
            consumer_kwargs["ucredentials"],
        )
        node = urgap.init_unode(consumer_kwargs["unode_full_identifier"])
        ufiles = urgap.UFileList.from_uri_list(consumer_kwargs["input_uris"])
        urd = urgap.URunDict(consumer_kwargs["urun_dict"])
        urd.wid = consumer_kwargs["wid"]
        urd.unode_parameters["remote_url"] = None
        urd["is_remote_run"] = False
        output_files = node.run(ufiles=ufiles, urun_dict=urd)
        output_uris = [o.as_uri() for o in output_files if o is not None]
        ok = True
    except Exception:
        logger.exception(
            "Failed to process message",
        )
    return ok, output_uris


def _service_bus_run_worker(
    cred_key: str,
    unode_identifier: str,
    shutdown_event: EventClass | None = None,
) -> None:
    """Run a Service Bus worker for a specific unode.

    Args:
        cred_key: URI containing the namespace (azure-servicebus://<namespace>.servicebus.windows.net).
        unode_identifier: Full unode identifier (e.g., Name:1.0.0).
        shutdown_event: Event to signal parent process to terminate.
    """
    from azure.identity import DefaultAzureCredential
    from azure.servicebus import (
        AutoLockRenewer,
        ServiceBusClient,
        ServiceBusReceiveMode,
    )

    namespace_host = cred_key.split("://", 1)[-1].rstrip("/")
    credential = DefaultAzureCredential()
    topic_name = urgap.config["service_bus_topic"]
    subscription_name = unode_identifier.replace(":", "__")
    completion_topic = urgap.config["service_bus_completion_topic"]
    exit_after_first = urgap.config["service_bus_exit_after_first_message"]
    max_autorenew = urgap.config["service_bus_max_autorenewal_minutes"] * 60
    topic_subscription_filter_pairs = [
        (topic_name, subscription_name, unode_identifier),
    ]
    if completion_topic is not None:
        topic_subscription_filter_pairs += [(completion_topic, "Completed", None)]
    _ensure_service_bus_entities(
        namespace_host,
        credential,
        topic_subscription_filter_pairs=topic_subscription_filter_pairs,
    )
    with ServiceBusClient(
        fully_qualified_namespace=namespace_host,
        credential=credential,
    ) as client:
        receiver_ctx = client.get_subscription_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
            max_wait_time=5,
            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
        )
        completion_sender = (
            client.get_topic_sender(topic_name=completion_topic)
            if completion_topic
            else None
        )
        renewer = AutoLockRenewer() if max_autorenew > 0 else None
        with receiver_ctx as receiver:
            logger.info(
                "ServiceBus worker started for unode=%s topic=%s subscription=%s max_autorenew=%ss",
                unode_identifier,
                topic_name,
                subscription_name,
                max_autorenew,
            )
            _handle_service_bus_messages(
                receiver=receiver,
                completion_sender=completion_sender,
                completion_topic=completion_topic if completion_sender else None,
                exit_after_first=exit_after_first,
                unode_identifier=unode_identifier,
                lock_renewer=renewer,
                max_autorenew=max_autorenew,
            )
        if renewer:
            renewer.close()
    if exit_after_first and shutdown_event:
        shutdown_event.set()


def _process_service_bus_message(
    msg: object,
    receiver: object,
    completion_sender: object | None,
    completion_topic: str | None,
    unode_identifier: str,
    exit_after_first: bool,
) -> bool:
    """Handle a single Service Bus message.

    Returns True if worker loop should stop; False otherwise.
    """
    preview = json.loads(str(msg))
    target_unode = preview.get("subscription_key")
    if target_unode != unode_identifier:
        receiver.abandon_message(msg)
        return False
    ok, output_uris = _process_message(preview)
    if ok:
        if completion_topic is not None:
            event_payload = preview.copy()
            if "custom_message" in event_payload:
                event_payload["custom_message"].update({"output_uris": output_uris})
            else:
                event_payload["custom_message"] = {"output_uris": output_uris}
            _publish_completion(
                completion_sender,
                completion_topic,
                event_payload,
            )
        receiver.complete_message(msg)
        if exit_after_first:
            logger.info(
                "Configured to exit after first message; stopping worker for %s",
                unode_identifier,
            )
            return True
    else:
        receiver.abandon_message(msg)
    return False


def _handle_service_bus_messages(
    receiver: object,
    completion_sender: object | None,
    completion_topic: str | None,
    exit_after_first: bool,
    unode_identifier: str,
    lock_renewer: object | None,
    max_autorenew: float,
) -> None:
    empty_polls = 0
    while True:
        messages = receiver.receive_messages(
            max_wait_time=5,
            max_message_count=1,
        )
        if not messages:
            empty_polls += 1
            if empty_polls >= 3:
                logger.info(
                    "No messages after %s consecutive polls exiting worker",
                    empty_polls,
                )
                return
            time.sleep(10)
            continue
        for msg in messages:
            if lock_renewer and max_autorenew > 0:
                lock_renewer.register(
                    receiver,
                    msg,
                    max_lock_renewal_duration=max_autorenew,
                )
            stop = _process_service_bus_message(
                msg,
                receiver,
                completion_sender,
                completion_topic,
                unode_identifier,
                exit_after_first,
            )
            if stop:
                return


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
@click.option(
    "--via-servicebus",
    help="Service Bus ucredentials key (azure-servicebus://<ns>.servicebus.windows.net) to run a subscription worker.",
    required=False,
)
def upi_server(
    nodes: tuple | str,
    mcp: bool | None,
    via_servicebus: str | None,
) -> None:
    """Spawn servers for requested Urgap nodes and optional Service Bus worker.

    If --via-servicebus is provided a worker process is started that listens on configured queues.
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
        if via_servicebus is not None:
            sb_proc = multiprocessing.Process(
                target=_service_bus_run_worker,
                args=(via_servicebus, unode, shutdown_event),
            )
            processes.append(sb_proc)
            sb_proc.start()

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
        logger.info(msg)
        shutdown_event.set()
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
