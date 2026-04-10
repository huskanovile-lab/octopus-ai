CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), email TEXT UNIQUE NOT NULL, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE workspaces (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), user_id UUID REFERENCES users(id), name TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE symbols (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), workspace_id UUID REFERENCES workspaces(id), ticker TEXT NOT NULL, venue TEXT, is_active BOOLEAN DEFAULT TRUE);

CREATE TABLE market_bars (id BIGSERIAL PRIMARY KEY, symbol_id UUID REFERENCES symbols(id), ts TIMESTAMPTZ NOT NULL, open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC, volume NUMERIC);
CREATE TABLE market_quotes (id BIGSERIAL PRIMARY KEY, symbol_id UUID REFERENCES symbols(id), ts TIMESTAMPTZ NOT NULL, bid NUMERIC, ask NUMERIC, bid_size NUMERIC, ask_size NUMERIC, spread_bps NUMERIC);
CREATE TABLE feature_snapshots (id BIGSERIAL PRIMARY KEY, symbol_id UUID REFERENCES symbols(id), ts TIMESTAMPTZ NOT NULL, payload JSONB NOT NULL);
CREATE TABLE tradeability_scores (id BIGSERIAL PRIMARY KEY, symbol_id UUID REFERENCES symbols(id), ts TIMESTAMPTZ NOT NULL, score NUMERIC, reasons JSONB);

CREATE TABLE strategies (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), name TEXT NOT NULL, status TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE strategy_versions (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), strategy_id UUID REFERENCES strategies(id), version TEXT NOT NULL, config JSONB NOT NULL, regime_eligibility JSONB);
CREATE TABLE agent_runs (id BIGSERIAL PRIMARY KEY, agent_name TEXT, started_at TIMESTAMPTZ, ended_at TIMESTAMPTZ, status TEXT, metrics JSONB);

CREATE TABLE signals (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), symbol_id UUID REFERENCES symbols(id), strategy_version_id UUID REFERENCES strategy_versions(id), ts TIMESTAMPTZ, side TEXT, payload JSONB);
CREATE TABLE signal_decisions (id BIGSERIAL PRIMARY KEY, signal_id UUID REFERENCES signals(id), status TEXT, reasons JSONB, confidence JSONB, decided_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE orders (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), signal_id UUID REFERENCES signals(id), type TEXT, status TEXT, qty NUMERIC, limit_price NUMERIC, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE fills (id BIGSERIAL PRIMARY KEY, order_id UUID REFERENCES orders(id), status TEXT, qty NUMERIC, price NUMERIC, fee NUMERIC, slippage_bps NUMERIC, fill_realism_score NUMERIC, ts TIMESTAMPTZ DEFAULT now());
CREATE TABLE positions (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), symbol_id UUID REFERENCES symbols(id), strategy_version_id UUID REFERENCES strategy_versions(id), side TEXT, qty NUMERIC, entry_price NUMERIC, stop_price NUMERIC, target_price NUMERIC, status TEXT, opened_at TIMESTAMPTZ, closed_at TIMESTAMPTZ);

CREATE TABLE portfolio_snapshots (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, equity NUMERIC, gross_exposure NUMERIC, net_exposure NUMERIC);
CREATE TABLE pnl_snapshots (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, daily_pnl NUMERIC, cumulative_pnl NUMERIC, drawdown NUMERIC, by_dims JSONB);
CREATE TABLE risk_events (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, event_type TEXT, payload JSONB);
CREATE TABLE governance_state (workspace_id UUID PRIMARY KEY REFERENCES workspaces(id), mode TEXT, global_risk_multiplier NUMERIC, emergency_pause BOOLEAN, updated_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE anomalies (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, anomaly_type TEXT, severity TEXT, payload JSONB);

CREATE TABLE knowledge_observations (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, scope TEXT, subject TEXT, metrics JSONB, confidence NUMERIC);
CREATE TABLE knowledge_conclusions (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, scope TEXT, subject TEXT, conclusion TEXT, status TEXT, confidence NUMERIC, expires_at TIMESTAMPTZ, revalidate_after TIMESTAMPTZ);
CREATE TABLE evaluations (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, metric_name TEXT, metric_value NUMERIC, dims JSONB);
CREATE TABLE backtest_runs (id BIGSERIAL PRIMARY KEY, strategy_version_id UUID REFERENCES strategy_versions(id), started_at TIMESTAMPTZ, ended_at TIMESTAMPTZ, result JSONB);
CREATE TABLE experiment_runs (id BIGSERIAL PRIMARY KEY, candidate_variant_id UUID, started_at TIMESTAMPTZ, ended_at TIMESTAMPTZ, result JSONB);
CREATE TABLE candidate_variants (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), strategy_id UUID REFERENCES strategies(id), status TEXT, hypothesis TEXT, created_at TIMESTAMPTZ DEFAULT now(), promoted_at TIMESTAMPTZ);

CREATE TABLE system_events (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ NOT NULL, event_name TEXT NOT NULL, source TEXT, payload JSONB NOT NULL);
CREATE TABLE audit_logs (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, actor TEXT, action TEXT, payload JSONB);
CREATE TABLE daily_summaries (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), trade_date DATE, payload JSONB, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE system_health_snapshots (id BIGSERIAL PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id), ts TIMESTAMPTZ, data_feed_quality NUMERIC, agent_responsiveness NUMERIC, signal_spam NUMERIC, execution_realism_drift NUMERIC, strategy_degradation NUMERIC, anomaly_pressure NUMERIC);
