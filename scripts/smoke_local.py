"""Verify the running local stack through the frontend's API proxy."""

import argparse
import json
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:5173")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    with urlopen(base, timeout=10) as response:
        html = response.read().decode("utf-8")
        if response.status != 200 or 'lang="vi"' not in html:
            raise SystemExit("Frontend UTF-8 Vietnamese shell check failed")
    for endpoint, expected in (("live", "ok"), ("ready", "ready")):
        with urlopen(f"{base}/api/v1/health/{endpoint}", timeout=10) as response:
            body = json.load(response)
            if response.status != 200 or body["status"] != expected:
                raise SystemExit(f"Health {endpoint} failed")
            print(f"PASS {endpoint}: HTTP {response.status}, status={body['status']}")
    print("PASS local frontend -> API -> PostgreSQL")


if __name__ == "__main__":
    main()
