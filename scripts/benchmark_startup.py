"""Measure independent local developer startup and stop all processes created here."""

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def measure(name, command, directory, port, health_path, log_directory):
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(f"Port {port} is already in use")
    started = time.perf_counter()
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    with (log_directory / f"{name}.log").open("wb") as log:
        process = subprocess.Popen(
            command,
            cwd=directory,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )
        try:
            while time.perf_counter() - started < 30:
                if process.poll() is not None:
                    raise RuntimeError(f"{name} exited; see {log_directory / (name + '.log')}")
                try:
                    with urlopen(f"http://127.0.0.1:{port}{health_path}", timeout=1) as response:
                        if response.status == 200:
                            return {
                                "service": name,
                                "command": command,
                                "port": port,
                                "seconds_to_http_200": round(time.perf_counter() - started, 3),
                            }
                except (URLError, TimeoutError, ConnectionError):
                    time.sleep(0.1)
            raise TimeoutError(f"{name} did not become available within 30 seconds")
        finally:
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".local/startup.json")
    args = parser.parse_args()
    log_directory = ROOT / ".local/startup-logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    python = ROOT / (
        "backend/.venv/Scripts/python.exe" if os.name == "nt" else "backend/.venv/bin/python"
    )
    results = [
        measure(
            "backend",
            [
                str(python),
                "-B",
                "-m",
                "app",
                "--host",
                "127.0.0.1",
                "--port",
                "58098",
            ],
            ROOT / "backend",
            58098,
            "/api/v1/health/live",
            log_directory,
        ),
        measure(
            "frontend",
            [
                "node",
                "node_modules/vite/bin/vite.js",
                "--host",
                "127.0.0.1",
                "--port",
                "5175",
                "--strictPort",
            ],
            ROOT / "frontend",
            5175,
            "/",
            log_directory,
        ),
    ]
    report = {
        "measured_at": datetime.now().astimezone().isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "node": subprocess.check_output(["node", "--version"], text=True).strip(),
        "method": (
            "Warm dependency caches. One independent process per service. "
            "Monotonic clock to first HTTP 200."
        ),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
