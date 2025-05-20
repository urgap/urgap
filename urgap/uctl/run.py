
import asyncio
import json
import logging
import multiprocessing
import os
import signal
import threading

from concurrent.futures import ProcessPoolExecutor
from types import FrameType
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse




def run_unode_in_loop(payload: dict, name: str) -> list:

    Args:
        payload: The JSON payload to configure the node execution.

    Returns:
        List of UFile UUris for output files.
    """
    uf = payload["ufiles"]
    ur["unode_parameters"]["remote_url"] = None
    return [o.as_uri() for o in output_files]


def create_app(name: str) -> FastAPI:
    """Create FastAPI app with /v1/run and /v1/terminate endpoints.

    Args:

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
        )
        loop = asyncio.get_running_loop()


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


@click.command()
@click.option(
    "--nodes",
    "-n",
    help="Nodes for which to start server.",
    required=True,
    multiple=True,
)

    """
    processes = []
    shutdown_event = multiprocessing.Event()
    nodes_list = get_all_relevant_nodes(nodes=nodes)
    for unode in nodes_list:
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

    def signal_handler(sig: int, _frame: FrameType | None) -> None:
        msg = f"Parent process received termination signal {sig}"
        for proc in processes:
            proc.terminate()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    for process in processes:
        process.join()