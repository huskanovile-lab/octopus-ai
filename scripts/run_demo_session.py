#!/usr/bin/env python3
"""Seed and run deterministic autonomous demo session."""
import os
from pathlib import Path

from fastapi.testclient import TestClient

from services.agents.src.main import build_app


def main() -> None:
    db_path = Path("services/agents/demo.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["DEMO_DB_PATH"] = str(db_path)
    app = build_app(start_loop=False)
    client = TestClient(app)

    for _ in range(8):
        client.post("/api/v1/demo/run-step")

    print("status", client.get("/api/v1/system/status").json())
    print("signals", len(client.get("/api/v1/signals").json()))
    print("rejected", len(client.get("/api/v1/signals/rejected").json()))
    print("fills", len(client.get("/api/v1/fills").json()))
    print("portfolio", client.get("/api/v1/portfolio/state").json())
    print("replay_events", len(client.get("/api/v1/replay/example").json()))
    print("Demo complete. Start API with uvicorn and open dashboard to watch live updates.")


if __name__ == "__main__":
    main()
