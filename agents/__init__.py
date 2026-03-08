"""Debate agents module - orchestrates multi-agent reasoning."""

from .debate import DebateOrchestrator
from .models import DebateResult, DebateRound, AgentRole

__all__ = ["DebateOrchestrator", "DebateResult", "DebateRound", "AgentRole"]
