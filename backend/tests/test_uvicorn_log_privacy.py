"""Exercise the actual HTTP server rather than TestClient-only logging."""

import asyncio
import logging
import socket

import uvicorn

from app.core.config import Settings
from app.main import create_app


def test_default_uvicorn_destinations_do_not_log_query_or_exception_details():
    async def exercise():
        config = uvicorn.Config(
            lambda: create_app(Settings(database_url=None, environment="test", _env_file=None)),
            factory=True,
            host="127.0.0.1",
            port=0,
            http="h11",
            lifespan="on",
        )
        # Install the synthetic failure only after the normal app factory runs.
        factory = config.app

        def with_failure():
            app = factory()

            @app.get("/synthetic-runtime-failure")
            async def fail():
                raise RuntimeError("synthetic-private-exception")

            return app

        config.app = with_failure
        records = []

        class Capture(logging.Handler):
            def emit(self, record):
                records.append(logging.Formatter().format(record))

        loggers = [logging.getLogger(name) for name in ("uvicorn.access", "uvicorn.error")]
        previous = [(logger.handlers[:], logger.propagate, logger.filters[:]) for logger in loggers]
        for logger in loggers:
            logger.handlers = [Capture()]
            logger.propagate = False
        server = uvicorn.Server(config)
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        listener.setblocking(False)
        port = listener.getsockname()[1]
        task = asyncio.create_task(server.serve(sockets=[listener]))
        responses = []
        try:
            for _ in range(200):
                if server.started or task.done():
                    break
                await asyncio.sleep(0.01)
            assert server.started
            for path in (
                "/api/v1/health/live?token=synthetic-private-query",
                "/synthetic-runtime-failure",
            ):
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
                try:
                    writer.write(
                        (
                            f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                        ).encode()
                    )
                    await writer.drain()
                    responses.append(await asyncio.wait_for(reader.read(), timeout=5))
                finally:
                    writer.close()
                    await writer.wait_closed()
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, timeout=5)
            listener.close()
            for logger, (handlers, propagate, filters) in zip(loggers, previous, strict=True):
                logger.handlers = handlers
                logger.propagate = propagate
                logger.filters = filters
        assert b"200 OK" in responses[0]
        assert b"500 Internal Server Error" in responses[1]
        combined = "\n".join(records)
        assert "synthetic-private-query" not in combined
        assert "synthetic-private-exception" not in combined
        assert any("runtime failure" in record.lower() for record in records)

    asyncio.run(exercise())
