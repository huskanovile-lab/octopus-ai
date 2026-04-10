"use client";

import { useEffect, useMemo, useState } from "react";

type TimelineEvent = { event: string; payload: Record<string, unknown> };
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const groups: Record<string, string> = {
  market_tick_received: "OBSERVE",
  regime_updated: "UNDERSTAND",
  feature_snapshot_created: "UNDERSTAND",
  tradeability_score_updated: "UNDERSTAND",
  signal_proposed: "DECIDE",
  signal_rejected: "DECIDE",
  signal_approved: "DECIDE",
  order_created: "ACT",
  order_filled: "ACT",
  pnl_updated: "REVIEW",
  knowledge_conclusion_created: "ADAPT",
  anomaly_detected: "RISK",
  heartbeat: "HEARTBEAT",
};

export function ControlRoom() {
  const [status, setStatus] = useState<any>({ ai_active: false, regime: "unknown", symbol: "AAPL", mode: "autonomous_paper_mode", signal_funnel: {} });
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [rejected, setRejected] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [portfolio, setPortfolio] = useState<any>({ equity: 0, unrealized_pnl: 0 });
  const [knowledge, setKnowledge] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>({});

  useEffect(() => {
    const ws = new WebSocket(`${API.replace("http", "ws")}/ws/system_timeline`);
    ws.onmessage = (m) => {
      const evt = JSON.parse(m.data);
      setEvents((prev) => [evt, ...prev].slice(0, 40));
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    const pull = async () => {
      const [s, r, p, pf, k, a, m] = await Promise.all([
        fetch(`${API}/api/v1/system/status`).then((x) => x.json()),
        fetch(`${API}/api/v1/signals/rejected`).then((x) => x.json()),
        fetch(`${API}/api/v1/positions`).then((x) => x.json()),
        fetch(`${API}/api/v1/portfolio/state`).then((x) => x.json()),
        fetch(`${API}/api/v1/knowledge/conclusions`).then((x) => x.json()),
        fetch(`${API}/api/v1/anomalies`).then((x) => x.json()),
        fetch(`${API}/api/v1/system/metrics`).then((x) => x.json()),
      ]);
      setStatus(s);
      setRejected(r);
      setPositions(p);
      setPortfolio(pf);
      setKnowledge(k);
      setAnomalies(a);
      setMetrics(m);
    };
    pull();
    const t = setInterval(pull, 1000);
    return () => clearInterval(t);
  }, []);

  const grouped = useMemo(() => {
    return events.map((e) => ({ ...e, group: groups[e.event] ?? "OTHER" }));
  }, [events]);

  const setMode = async (mode: string) => {
    await fetch(`${API}/api/v1/system/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    });
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <section className="rounded-2xl border border-white/20 bg-white/10 backdrop-blur-xl p-4">
        <h1 className="text-2xl font-semibold">Mission Control</h1>
        <p>AI {status.ai_active ? "ACTIVE" : "PAUSED"} | Symbol {status.symbol} | Regime {status.regime} | Mode {status.mode}</p>
        <div className="flex gap-2 mt-2 text-xs">
          {["observer_mode", "supervised_paper_mode", "autonomous_paper_mode", "defensive_mode", "paused_mode"].map((m) => (
            <button key={m} className="px-2 py-1 border border-cyan-500/40 rounded" onClick={() => setMode(m)}>{m}</button>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
        <div className="rounded-xl border border-cyan-400/20 p-3">Signal Funnel: P {status.signal_funnel?.proposed ?? 0} / A {status.signal_funnel?.approved ?? 0} / R {status.signal_funnel?.rejected ?? 0}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Portfolio: Eq {portfolio.equity?.toFixed?.(2)} | UPNL {portfolio.unrealized_pnl?.toFixed?.(2)}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Rejected Signals: {rejected.length}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Open Positions: {positions.length}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Knowledge: {knowledge[0]?.conclusion ?? "-"}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Anomalies: {anomalies[0]?.anomaly_type ?? "none"}</div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
        <div className="rounded-xl border border-cyan-400/20 p-3">Heartbeat: {metrics.heartbeat_count ?? 0} | Loop: {metrics.loop_count ?? 0}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Execution: fills {metrics.execution_metrics?.fills ?? 0} avgSlip {Number(metrics.execution_metrics?.avg_slippage_bps ?? 0).toFixed(3)}</div>
      </div>

      <div className="rounded-xl border border-cyan-400/20 p-3 mt-4 max-h-72 overflow-auto text-xs">
        {grouped.map((e, i) => (
          <div key={i} className="py-1 border-b border-white/5">[{e.group}] {e.event}</div>
        ))}
      </div>
    </main>
  );
}
