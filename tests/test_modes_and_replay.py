import os

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from services.agents.src.main import build_app


def test_modes_change_runtime_behavior(tmp_path):
    os.environ["DEMO_DB_PATH"] = str(tmp_path / "modes.db")
    app = build_app(start_loop=False)
    c = TestClient(app)

    c.post("/api/v1/system/mode", json={"mode": "paused_mode"})
    assert c.post("/api/v1/demo/run-step").json()["status"] == "paused"

    c.post("/api/v1/system/mode", json={"mode": "observer_mode"})
    step = c.post("/api/v1/demo/run-step").json()
    assert step["status"] == "rejected"
    assert "mode_blocks_execution" in step["reasons"]

    c.post("/api/v1/system/mode", json={"mode": "autonomous_paper_mode"})
    for _ in range(6):
        c.post("/api/v1/demo/run-step")
    assert len(c.get("/api/v1/fills").json()) > 0


def test_replay_chain_invariants(tmp_path):
    os.environ["DEMO_DB_PATH"] = str(tmp_path / "replay.db")
    app = build_app(start_loop=False)
    c = TestClient(app)
    for _ in range(8):
        c.post("/api/v1/demo/run-step")
    replay = c.get("/api/v1/replay/example").json()
    assert replay["invariants"]["ordered_prefix"] is True
    assert replay["invariants"]["decision_terminal_present"] is True
    assert len(replay["events"]) >= 6
