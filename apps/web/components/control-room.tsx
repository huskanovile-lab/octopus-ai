export function ControlRoom() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <section className="rounded-2xl border border-white/20 bg-white/10 backdrop-blur-xl p-4">
        <h1 className="text-2xl font-semibold">Mission Control — Autonomous Paper Trading OS</h1>
        <p className="text-slate-300 mt-2">
          AI swarm is active: observing market, classifying regimes, ranking opportunities, rejecting weak setups, and simulating paper execution.
        </p>
      </section>

      <section className="grid grid-cols-4 gap-4 mt-4">
        {[
          "AI Activity Stream",
          "Opportunity Radar",
          "Signal Funnel",
          "Agent Swarm",
          "Live Trading Workspace",
          "Portfolio Pulse",
          "Risk Perimeter",
          "Strategy Brain",
          "Knowledge Vault",
          "Research Lab",
          "Replay Console",
          "System Health"
        ].map((name) => (
          <div key={name} className="rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-3 min-h-28">
            <h2 className="font-medium">{name}</h2>
            <p className="text-xs text-slate-400 mt-2">Always-on autonomous stream enabled.</p>
          </div>
        ))}
      </section>
    </main>
  );
}
