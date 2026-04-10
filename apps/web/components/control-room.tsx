"use client";

import { useEffect, useMemo, useState } from "react";

type TimelineEvent = { event: string; payload: Record<string, unknown> };

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function ControlRoom() {
  const [status, setStatus] = useState<any>({ ai_active: false, regime: "unknown", symbol: "AAPL" });
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [rejected, setRejected] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [portfolio, setPortfolio] = useState<any>({ equity: 0, unrealized_pnl: 0 });
  const [knowledge, setKnowledge] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket(`${API.replace("http", "ws")}/ws/system_timeline`);
    ws.onmessage = (m) => {
      const evt = JSON.parse(m.data);
      setEvents((prev) => [evt, ...prev].slice(0, 20));
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    const pull = async () => {
      const [s, r, p, pf, k, a] = await Promise.all([
        fetch(`${API}/api/v1/system/status`).then((x) => x.json()),
        fetch(`${API}/api/v1/signals/rejected`).then((x) => x.json()),
        fetch(`${API}/api/v1/positions`).then((x) => x.json()),
        fetch(`${API}/api/v1/portfolio/state`).then((x) => x.json()),
        fetch(`${API}/api/v1/knowledge/conclusions`).then((x) => x.json()),
        fetch(`${API}/api/v1/anomalies`).then((x) => x.json()),
      ]);
      setStatus(s);
      setRejected(r);
      setPositions(p);
      setPortfolio(pf);
      setKnowledge(k);
      setAnomalies(a);
    };
    pull();
    const t = setInterval(pull, 1000);
    return () => clearInterval(t);
  }, []);

  const funnel = useMemo(() => {
    const proposed = events.filter((e) => e.event === "signal_proposed").length;
    const approved = events.filter((e) => e.event === "signal_approved").length;
    const rej = events.filter((e) => e.event === "signal_rejected").length;
    return { proposed, approved, rejected: rej };
  }, [events]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <section className="rounded-2xl border border-white/20 bg-white/10 backdrop-blur-xl p-4">
        <h1 className="text-2xl font-semibold">Mission Control</h1>
        <p>AI is {status.ai_active ? "ACTIVE" : "INACTIVE"} | Symbol: {status.symbol} | Regime: {status.regime}</p>
      </section>
      <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
        <div className="rounded-xl border border-cyan-400/20 p-3">Signal Funnel: P {funnel.proposed} / A {funnel.approved} / R {funnel.rejected}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Portfolio Equity: {portfolio.equity?.toFixed?.(2)} | UPNL: {portfolio.unrealized_pnl?.toFixed?.(2)}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Rejected Signals: {rejected.length}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Open Positions: {positions.length}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Knowledge: {knowledge[0]?.conclusion ?? "-"}</div>
        <div className="rounded-xl border border-cyan-400/20 p-3">Anomalies: {anomalies[0]?.anomaly_type ?? "none"}</div>
      </div>
      <div className="rounded-xl border border-cyan-400/20 p-3 mt-4 max-h-64 overflow-auto">
        {events.map((e, i) => (
          <div key={i}>{e.event}</div>
        ))}
      </div>
    </main>
  );
}
