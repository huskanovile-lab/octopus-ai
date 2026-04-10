from services.execution_sim.src.simulator import Order, simulate_lifecycle


def test_execution_lifecycle_transitions():
    events = simulate_lifecycle(Order(symbol="AAPL", side="buy", qty=10, order_type="market"), 100, 8, seed=7)
    assert events[0]["status"] == "accepted"
    assert events[-1]["status"] in {"filled", "partially_filled"}
    total = sum(e["qty"] for e in events[1:])
    assert total == 10
