from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ConfidenceVector(BaseModel):
    regime_confidence: float = Field(ge=0, le=1)
    strategy_fit_confidence: float = Field(ge=0, le=1)
    signal_confidence: float = Field(ge=0, le=1)
    risk_approval_confidence: float = Field(ge=0, le=1)
    execution_confidence: float = Field(ge=0, le=1)
    knowledge_confidence: float = Field(ge=0, le=1)


class EventEnvelope(BaseModel):
    id: str
    ts: datetime
    workspace_id: str
    event: str
    source: str
    payload: dict[str, Any]


class SignalDecision(BaseModel):
    signal_id: str
    status: Literal["approved", "rejected"]
    reasons: list[str] = []
    confidence: ConfidenceVector


class GovernanceState(BaseModel):
    mode: Literal[
        "observer_mode",
        "supervised_paper_mode",
        "autonomous_paper_mode",
        "defensive_mode",
        "paused_mode",
    ] = "autonomous_paper_mode"
    global_risk_multiplier: float = 1.0
    emergency_pause: bool = False
