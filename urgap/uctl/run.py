
import asyncio
import logging
import multiprocessing
import signal
import threading
from fastapi.responses import JSONResponse



def create_app(name: str) -> FastAPI:

    @app.post("/v1/run")
    async def run_unode(request: Request) -> JSONResponse:
        payload = await request.json()


    @app.post("/v1/terminate")
        app.state.shutdown_event.set()
        return {"message": "Server shutdown initiated."}

    return app



    """
    app = create_app(name)
    app.state.shutdown_event = shutdown_event
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.start()

    shutdown_event.wait()

    server.should_exit = True
    thread.join()

@click.command()
@click.option(
)

    """
    processes = []
    shutdown_event = multiprocessing.Event()
        p = multiprocessing.Process(
            target=run_server,
            args=(
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