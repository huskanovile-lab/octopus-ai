export type AutonomyMode =
  | "observer_mode"
  | "supervised_paper_mode"
  | "autonomous_paper_mode"
  | "defensive_mode"
  | "paused_mode";

export type ConfidenceVector = {
  regimeConfidence: number;
  strategyFitConfidence: number;
  signalConfidence: number;
  riskApprovalConfidence: number;
  executionConfidence: number;
  knowledgeConfidence: number;
};

export type EventName =
  | "market_tick_received"
  | "bar_closed"
  | "feature_snapshot_created"
  | "tradeability_score_updated"
  | "regime_updated"
  | "strategy_selected"
  | "signal_proposed"
  | "signal_rejected"
  | "signal_approved"
  | "order_created"
  | "order_filled"
  | "position_opened"
  | "position_closed"
  | "pnl_updated"
  | "risk_limit_hit"
  | "anomaly_detected"
  | "governance_mode_changed"
  | "knowledge_conclusion_created"
  | "candidate_variant_created"
  | "candidate_variant_promoted"
  | "daily_summary_generated";

export interface EventEnvelope<T = unknown> {
  id: string;
  ts: string;
  workspaceId: string;
  event: EventName;
  source: string;
  payload: T;
}

export interface SignalRejectedPayload {
  symbol: string;
  strategy: string;
  reasonCodes: string[];
  confidence: ConfidenceVector;
}
