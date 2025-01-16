
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
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.start()

    server.should_exit = True
    thread.join()

@click.command()

    """
    processes = []
            target=run_server,
            args=(
                port,
            ),
        )

