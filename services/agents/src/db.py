from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Database:
    path: str = "services/agents/demo.db"

    def __post_init__(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    ts TEXT,
                    symbol TEXT,
                    strategy TEXT,
                    side TEXT,
                    status TEXT,
                    reasons TEXT,
                    confidence REAL
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    signal_id TEXT,
                    ts TEXT,
                    status TEXT,
                    qty INTEGER,
                    symbol TEXT
                );
                CREATE TABLE IF NOT EXISTS fills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    ts TEXT,
                    status TEXT,
                    qty INTEGER,
                    price REAL,
                    fee REAL,
                    slippage_bps REAL,
                    realism REAL
                );
                CREATE TABLE IF NOT EXISTS positions (
                    symbol TEXT PRIMARY KEY,
                    qty INTEGER,
                    avg_price REAL,
                    unrealized_pnl REAL,
                    realized_pnl REAL,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT,
                    equity REAL,
                    cash REAL,
                    unrealized_pnl REAL,
                    realized_pnl REAL
                );
                CREATE TABLE IF NOT EXISTS knowledge_conclusions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT,
                    conclusion TEXT,
                    evidence TEXT,
                    confidence REAL,
                    stale_after_ts TEXT,
                    status TEXT
                );
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT,
                    anomaly_type TEXT,
                    detail TEXT
                );
                """
            )

    def insert_event(self, ts: str, event_name: str, payload: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO system_events(ts,event_name,payload) VALUES(?,?,?)",
                (ts, event_name, json.dumps(payload)),
            )
