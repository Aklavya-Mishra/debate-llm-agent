"""Debate agents module - orchestrates multi-agent reasoning."""

from agents.debate import DebateOrchestrator
from agents.models import DebateResult, DebateRound, AgentRole

__all__ = ["DebateOrchestrator", "DebateResult", "DebateRound", "AgentRole"]
