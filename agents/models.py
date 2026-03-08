"""Data models for the debate system."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Roles in the debate system."""
    PROPOSER = "proposer"
    CRITIC = "critic"
    SYNTHESIZER = "synthesizer"


class DebateMessage(BaseModel):
    """A single message in the debate."""
    role: AgentRole
    content: str
    reasoning: Optional[str] = None


class DebateRound(BaseModel):
    """A complete round of debate."""
    round_number: int
    proposal: str
    critique: str
    revision: str
    improvement_notes: Optional[str] = None


class DebateResult(BaseModel):
    """Final result of the debate process."""
    question: str
    rounds: list[DebateRound] = Field(default_factory=list)
    final_answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str
    total_tokens_used: int = 0


class DebateConfig(BaseModel):
    """Configuration for debate behavior."""
    max_rounds: int = Field(default=2, ge=1, le=5)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: str = "gpt-4o-mini"
    enable_streaming: bool = True
