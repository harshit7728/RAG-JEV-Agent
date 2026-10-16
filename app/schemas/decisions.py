
from typing import Literal

from pydantic import BaseModel, Field


class RoutingDecision(BaseModel):
    category: Literal[
        "knowledge",
        "greeting",
        "unsupported",
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class EvidenceDecision(BaseModel):
    sufficient: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class ApprovalDecision(BaseModel):
    requires_approval: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
