
import asyncio
import json
import logging
import multiprocessing
import signal
import threading
from fastapi.responses import JSONResponse



    uf = payload["ufiles"]
    ur["unode_parameters"]["remote_url"] = None

def create_app(name: str) -> FastAPI:
    app = FastAPI(title=name)
    app.state.name = name

    @app.post("/v1/run")
    async def run_unode(request: Request) -> JSONResponse:
        payload = await request.json()
        payload = json.loads(
            payload,
        )
        loop = asyncio.get_running_loop()


    @app.post("/v1/terminate")
        app.state.shutdown_event.set()
        return {"message": "Server shutdown initiated."}

    @app.get("/livez")
        return JSONResponse(status_code=200, content={"status": "livez"})

    @app.get("/readyz")
        return JSONResponse(status_code=200, content={"status": "readyz"})

    return app



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

        for proc in processes:
            proc.terminate()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    for process in processes:
        process.join()