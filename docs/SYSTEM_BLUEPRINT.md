# Autonomous AI Paper Trading OS Blueprint

## 1) System architecture
- **Control plane + data plane split**.
- **Always-on agent loop**: Observe → Understand → Decide → Act → Review → Adapt.
- **Event-driven backbone** (Redis Streams in v1, Kafka-ready abstraction).
- **Paper-only execution** with realism model (spread, slippage, latency, partial fills, fees).
- **Replay-first** architecture using append-only `system_events` and deterministic projection pipelines.
- **Operator governance** with autonomy modes:
  - `observer_mode`
  - `supervised_paper_mode`
  - `autonomous_paper_mode`
  - `defensive_mode`
  - `paused_mode`

## 2) Monorepo structure
- `/apps/web` — Next.js dashboard (glassmorphism control room).
- `/services/market-data` — quote/bar ingestion + quality checks.
- `/services/feature-engine` — feature pipelines + tradeability scoring.
- `/services/agents` — orchestrator + strategy + signal funnel.
- `/services/execution-sim` — realistic paper execution.
- `/services/portfolio` — positions, PnL, exposure.
- `/services/research` — candidate variants + shadow promotion.
- `/services/knowledge` — structured observations/conclusions.
- `/services/governance` — policy engine, mode switching, emergency controls.
- `/packages/shared-types` — typed events/contracts.
- `/packages/shared-config` — environment/runtime config.
- `/packages/shared-ui` — shared UI primitives/tokens.
- `/infrastructure` — docker/sql/bootstrap.

## 3) Database schema
Defined in `infrastructure/postgres/schema.sql` with key tables:
`users, workspaces, symbols, market_bars, market_quotes, feature_snapshots, tradeability_scores, strategies, strategy_versions, agent_runs, signals, signal_decisions, orders, fills, positions, portfolio_snapshots, pnl_snapshots, risk_events, governance_state, anomalies, knowledge_observations, knowledge_conclusions, evaluations, backtest_runs, experiment_runs, candidate_variants, system_events, audit_logs, daily_summaries, system_health_snapshots`.

## 4) Shared types and events
`packages/shared-types/src/events.ts` includes:
- Typed payload map for required events:
  `market_tick_received, bar_closed, feature_snapshot_created, tradeability_score_updated, regime_updated, strategy_selected, signal_proposed, signal_rejected, signal_approved, order_created, order_filled, position_opened, position_closed, pnl_updated, risk_limit_hit, anomaly_detected, governance_mode_changed, knowledge_conclusion_created, candidate_variant_created, candidate_variant_promoted, daily_summary_generated`.
- Confidence decomposition:
  `regimeConfidence, strategyFitConfidence, signalConfidence, riskApprovalConfidence, executionConfidence, knowledgeConfidence`.

## 5) Service responsibilities
- **market-data**: ingest, normalize, detect stale/abnormal feed.
- **feature-engine**: returns, vol, ATR, VWAP distance, z-score, momentum windows, breakout distance, spread, volume expansion/relative volume, session/regime features.
- **agents**: multi-agent coordination (Scout, Regime, Strategy Selector, Signal, Risk, Execution, Position Manager, Portfolio, Research, Learning, Oversight, Governance).
- **execution-sim**: order lifecycle + realism score.
- **portfolio**: exposures, drawdown, directional constraints, limits.
- **research**: shadow tests, candidate promotion/rollback.
- **knowledge**: scoped conclusions with expiry/revalidation.
- **governance**: autonomy modes, global pause, defensive reductions.

## 6) REST routes
Implemented starter endpoints in `services/agents/src/routers/*`:
- `/api/v1/symbols`
- `/api/v1/strategies`
- `/api/v1/agents/status`
- `/api/v1/signals`
- `/api/v1/signals/rejected`
- `/api/v1/orders`
- `/api/v1/fills`
- `/api/v1/positions`
- `/api/v1/portfolio/state`
- `/api/v1/risk/state`
- `/api/v1/governance/mode`
- `/api/v1/anomalies`
- `/api/v1/experiments`
- `/api/v1/knowledge/conclusions`
- `/api/v1/daily-summaries`
- `/api/v1/replay/sessions`
- `/api/v1/system/events`
- `/api/v1/system/health`

## 7) WebSocket channels
`services/agents/src/ws/manager.py` defines channels:
- `market_stream`
- `agent_activity`
- `signal_funnel`
- `rejected_signals`
- `order_updates`
- `positions`
- `portfolio_updates`
- `risk_alerts`
- `anomalies`
- `governance_state`
- `system_timeline`
- `knowledge_updates`

## 8) Agent orchestration
- Tick scheduler emits `market_tick_received`.
- Pipeline stages:
  1. Scout + Market Regime classify context.
  2. Strategy Selector chooses active strategy or no-trade.
  3. Signal Agent proposes setup.
  4. Risk Agent approves/rejects.
  5. Execution Simulation Agent simulates.
  6. Position/Portfolio Agents maintain state.
  7. Learning/Research evaluate active vs shadow.
  8. Oversight/Governance enforce safety.
- Rejected signals are first-class persisted outcomes with explicit reasons.

## 9) Risk design
- Max daily/session DD.
- Max open positions.
- Symbol + gross exposure caps.
- Directional bias control.
- Liquidity/spread rejection.
- Cooldowns + consecutive loss guard.
- Strategy pause + symbol blocklist.
- Global emergency pause.
- Anomaly-triggered risk reduction.

## 10) Execution simulator design
- Supports market + limit orders.
- State machine: `accepted | partially_filled | filled | cancelled | rejected`.
- Models spread-crossing, slippage, latency, partial fills, fees.
- Computes `fill_realism_score` for monitoring drift.

## 11) Knowledge system design
- Structured facts, not chat memory.
- Observation record: metrics + confidence + scope + timestamps.
- Conclusion record: status lifecycle (`active`, `weak`, `stale`, `invalidated`) + expiry/revalidation.
- Link conclusions to evidence and performance shifts.

## 12) Dashboard information architecture
- Left: navigation, symbols, strategies, mode toggles.
- Top: global status/command bar.
- Center: Mission Control + charts/workspaces.
- Right: reasoning + decision chains.
- Bottom dock: logs/fills/anomalies/system timeline.
- Sections included:
  Mission Control, AI Activity Stream, Opportunity Radar, Signal Funnel, Agent Swarm, Live Trading Workspace, Portfolio Pulse, Risk Perimeter, Strategy Brain, Knowledge Vault, Research Lab, Replay Console.

## 13) File-by-file scaffold plan
See `docs/FILE_SCAFFOLD_PLAN.md`.

## 14) Starter code for critical modules
- FastAPI core app + routers.
- Async orchestrator loop.
- Event bus interface.
- Risk engine starter.
- Execution simulator starter.
- Feature engine starter indicators.
- Daily operating report generator.
- System health monitor.
- Frontend control-room shell.
