"""Synthetic audit probes. Run with backend venv Python from repository root.

Starts one loopback ephemeral HTTP socket, then shuts it down. Does not load
environment files or connect to a database. JSON output contains only booleans.
"""

import asyncio
import json
import logging
import socket
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "backend"))

import uvicorn

from app.core.config import Settings
from app.main import create_app
from app.modules.analytics.chart_input import ChartInput
from app.modules.school_calendar.domain import ScheduleTemplate
from app.modules.timetables.snapshot import SchedulingInputSnapshot


class Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(logging.Formatter().format(record))


async def probe_runtime():
    app = create_app(Settings(database_url=None, environment="test", _env_file=None))

    @app.get("/audit-synthetic-error")
    async def fail():
        raise RuntimeError("synthetic-private-exception-marker")

    config = uvicorn.Config(app, host="127.0.0.1", port=0, loop="asyncio", http="h11")
    capture = Capture()
    loggers = [logging.getLogger("uvicorn.access"), logging.getLogger("uvicorn.error")]
    previous = [(logger.handlers[:], logger.propagate) for logger in loggers]
    for logger in loggers:
        logger.handlers = [capture]
        logger.propagate = False
    server = uvicorn.Server(config)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.setblocking(False)
    port = listener.getsockname()[1]
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        for _ in range(200):
            if server.started or task.done():
                break
            await asyncio.sleep(0.01)
        if not server.started:
            raise RuntimeError("Synthetic probe server did not start")
        for target in (
            "/api/v1/health/live?token=synthetic-private-query-marker",
            "/audit-synthetic-error",
        ):
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(f"GET {target} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode())
            await writer.drain()
            await asyncio.wait_for(reader.read(), timeout=5)
            writer.close()
            await writer.wait_closed()
        output = "\n".join(capture.records)
        return {
            "uvicorn_logs_raw_query": "synthetic-private-query-marker" in output,
            "uvicorn_logs_exception_detail": "synthetic-private-exception-marker" in output,
        }
    finally:
        server.should_exit = True
        await asyncio.wait_for(task, timeout=5)
        listener.close()
        for logger, (handlers, propagate) in zip(loggers, previous):
            logger.handlers = handlers
            logger.propagate = propagate


def probe_domain():
    def accepts(factory):
        try:
            factory()
        except (TypeError, ValueError):
            return False
        return True

    slots = []
    mutable_filter = {"field": "full_name", "values": ["synthetic-name"]}
    mutable_assignment = {"teacher_id": "synthetic-before"}
    return {
        "schedule_template_changed_through_original_list": accepts(
            lambda: ScheduleTemplate(uuid4(), uuid4(), slots)
        ),
        "chart_accepts_missing_year": accepts(lambda: ChartInput(None, None, "grade_level")),
        "chart_accepts_unvalidated_filter": accepts(
            lambda: ChartInput(uuid4(), None, "grade_level", filters=(mutable_filter,))
        ),
        "snapshot_nested_element_changed": accepts(
            lambda: SchedulingInputSnapshot(
                uuid4(), uuid4(), uuid4(), (mutable_assignment,), (), (), (), ()
            )
        ),
    }


if __name__ == "__main__":
    print(json.dumps({**probe_domain(), **asyncio.run(probe_runtime())}, sort_keys=True))
