"""Re-measure P6: liveness latency while concurrent failed logins run Argon2 in the event loop.

Pings /health/live every ~5 ms for the whole burst and records the worst latency, so the
measurement does not depend on when the single ping happens to be scheduled.
Run like probe_live.py (needs dsn.sh). Synthetic identities only.
"""
import asyncio
import json
import os
import time
from pathlib import Path
from uuid import uuid4

import httpx2
from pydantic import SecretStr

from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.db.connection import Database
from app.main import create_app

RUNTIME_SQLA = os.environ["EDUOPS_TEST_RUNTIME_DSN"].replace(
    "postgresql://", "postgresql+psycopg://", 1
)


async def measure(concurrent_logins: int) -> dict:
    app = create_app(Settings(database_url=RUNTIME_SQLA, environment="test", _env_file=None))
    app.state.database = Database(SecretStr(RUNTIME_SQLA))
    run = uuid4().hex[:8]
    latencies: list[float] = []
    done = asyncio.Event()
    async with httpx2.AsyncClient(
        transport=httpx2.ASGITransport(app=app), base_url="https://testserver"
    ) as client:
        await client.get("/api/v1/health/live")

        async def pinger():
            while not done.is_set():
                start = time.perf_counter()
                await client.get("/api/v1/health/live")
                latencies.append((time.perf_counter() - start) * 1000)
                await asyncio.sleep(0.005)

        async def failed_login(index: int) -> int:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": f"p6b-{index}-{run}@example.com", "password": "x"},
            )
            return response.status_code

        ping_task = asyncio.create_task(pinger())
        await asyncio.sleep(0.05)
        burst_start = time.perf_counter()
        statuses = await asyncio.gather(*(failed_login(i) for i in range(concurrent_logins)))
        burst_ms = (time.perf_counter() - burst_start) * 1000
        done.set()
        await ping_task
    await app.state.database.close()
    return {
        "concurrent_logins": concurrent_logins,
        "statuses": sorted(set(statuses)),
        "burst_wall_ms": round(burst_ms, 1),
        "liveness_samples": len(latencies),
        "liveness_median_ms": round(sorted(latencies)[len(latencies) // 2], 1),
        "liveness_max_ms": round(max(latencies), 1),
    }


async def main() -> list[dict]:
    return [await measure(1), await measure(10)]


if __name__ == "__main__":
    output = asyncio.run(main(), loop_factory=create_event_loop)
    Path(__file__).with_name("probe_loop.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, indent=2))
