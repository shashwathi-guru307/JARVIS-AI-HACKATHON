from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


IncidentStatus = Literal[
    "DETECTED", "CORRELATING", "INVESTIGATING", "ASSESSED",
    "AWAITING_APPROVAL", "APPROVED", "REJECTED", "REMEDIATING",
    "VERIFYING", "RESOLVED", "FAILED",
]
ApprovalStatus = Literal["NOT_REQUIRED", "PENDING", "APPROVED", "REJECTED"]
ActionStatus = Literal["NOT_STARTED", "READY", "EXECUTING", "COMPLETED", "FAILED"]
VerificationStatus = Literal["NOT_STARTED", "PENDING", "VERIFIED", "REQUIRES_REVIEW"]


class RemediationStep(BaseModel):
    action_id: str
    description: str
    reason: str
    expected_effect: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    approval_required: bool
    safe_to_simulate: bool


class Incident(BaseModel):
    incident_id: str
    created_at: datetime
    updated_at: datetime
    title: str
    plant: str = "Smart Manufacturing Plant"
    production_line: str = "Assembly Line A"
    machine_id: str = "M-101"
    machine_name: str = "M-101"
    machine_type: str = "Industrial rotating production machine"
    machine_criticality: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"
    status: IncidentStatus
    severity: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_score: float = Field(..., ge=0, le=100)
    source_event_ids: list[str] = Field(default_factory=list)
    affected_components: list[str] = Field(default_factory=list)
    correlated_conditions: list[str] = Field(default_factory=list)
    investigation_summary: str = ""
    probable_root_causes: list[str] = Field(default_factory=list)
    root_cause_confidence: float = Field(0, ge=0, le=1)
    business_impact: dict[str, Any] = Field(default_factory=dict)
    operational_impact: dict[str, Any] = Field(default_factory=dict)
    recommended_remediation: str = ""
    remediation_steps: list[RemediationStep] = Field(default_factory=list)
    approval_required: bool = True
    approval_status: ApprovalStatus = "PENDING"
    action_status: ActionStatus = "NOT_STARTED"
    verification_status: VerificationStatus = "NOT_STARTED"
    verification_summary: str = ""
    audit_event_ids: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    verification: dict[str, Any] = Field(default_factory=dict)