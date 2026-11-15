import argparse

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run the EduOps 360 local API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        loop="app.core.event_loop:create_event_loop",
    )


if __name__ == "__main__":
    main()
