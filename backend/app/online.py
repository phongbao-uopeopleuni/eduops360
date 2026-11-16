"""Container entrypoint honoring Railway's injected listening port."""

import os

import uvicorn


def main():
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        loop="app.core.event_loop:create_event_loop",
    )


if __name__ == "__main__":
    main()
