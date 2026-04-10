import os
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from services.agents.src.main import build_app


def test_signal_to_execution_to_portfolio_flow(tmp_path):
    os.environ["DEMO_DB_PATH"] = str(tmp_path / "demo.db")
    app = build_app(start_loop=False)
    client = TestClient(app)
    for _ in range(6):
        client.post("/api/v1/demo/run-step")
    signals = client.get("/api/v1/signals").json()
    fills = client.get("/api/v1/fills").json()
    portfolio = client.get("/api/v1/portfolio/state").json()
    assert any(s["status"] == "approved" for s in signals)
    assert len(fills) > 0
    assert portfolio["equity"] > 0


def test_rejected_signal_path(tmp_path):
    os.environ["DEMO_DB_PATH"] = str(tmp_path / "demo2.db")
    app = build_app(start_loop=False)
    client = TestClient(app)
    client.post("/api/v1/demo/run-step")
    rej = client.get("/api/v1/signals/rejected").json()
    assert len(rej) >= 1
    assert len(rej[0]["reasons"]) >= 1


def test_websocket_event_emission(tmp_path):
    os.environ["DEMO_DB_PATH"] = str(tmp_path / "demo3.db")
    app = build_app(start_loop=False)
    client = TestClient(app)
    with client.websocket_connect("/ws/system_timeline") as ws:
        client.post("/api/v1/demo/run-step")
        data = ws.receive_json()
        assert "event" in data
