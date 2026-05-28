from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

class Source(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None

class Signal(BaseModel):
    type: str  # e.g., HIRING_SPIKE, BREACH_MENTION, EXEC_CHANGE, PRICING_CHANGE
    entity: str
    detail: str
    severity: int = Field(..., ge=1, le=10)  # Severity score 1-10
    source_url: str

class Entity(BaseModel):
    name: str
    type: str  # COMPANY, PERSON, DOMAIN, VULNERABILITY
    mentions: int = 1

class IntelligenceReport(BaseModel):
    target: str
    risk_score: float = Field(..., ge=0.0, le=10.0)  # 0-10
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    executive_summary: str
    signals: List[Signal] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    prior_context: str = ""  # from Cognee memory
    workflows_triggered: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class InvestigationRequest(BaseModel):
    target: str
    focus: List[str] = Field(default_factory=list)
