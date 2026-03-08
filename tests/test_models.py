"""Tests for the debate agent."""

import pytest
from agents.models import DebateConfig, DebateRound, DebateResult


class TestModels:
    """Test data models."""
    
    def test_debate_config_defaults(self):
        """Test DebateConfig has sensible defaults."""
        config = DebateConfig()
        assert config.max_rounds == 2
        assert config.temperature == 0.7
        assert config.model == "gpt-4o-mini"
    
    def test_debate_config_validation(self):
        """Test DebateConfig validates bounds."""
        # Valid config
        config = DebateConfig(max_rounds=3, temperature=0.5)
        assert config.max_rounds == 3
        
        # Invalid - too many rounds
        with pytest.raises(ValueError):
            DebateConfig(max_rounds=10)
        
        # Invalid - negative temperature
        with pytest.raises(ValueError):
            DebateConfig(temperature=-0.1)
    
    def test_debate_round_model(self):
        """Test DebateRound model."""
        round = DebateRound(
            round_number=1,
            proposal="Initial proposal",
            critique="Some critique",
            revision="Revised answer"
        )
        assert round.round_number == 1
        assert round.proposal == "Initial proposal"
    
    def test_debate_result_model(self):
        """Test DebateResult model."""
        result = DebateResult(
            question="Test question",
            final_answer="Final answer",
            confidence=0.85,
            reasoning_summary="Summary"
        )
        assert result.question == "Test question"
        assert result.confidence == 0.85
        assert result.rounds == []


class TestPrompts:
    """Test prompt templates."""
    
    def test_proposer_prompt_format(self):
        """Test PROPOSER_PROMPT can be formatted."""
        from prompts.templates import PROPOSER_PROMPT
        
        formatted = PROPOSER_PROMPT.format(
            question="What is Python?",
            revision_context="",
            answer_type="initial answer"
        )
        assert "What is Python?" in formatted
        assert "initial answer" in formatted
    
    def test_critic_prompt_format(self):
        """Test CRITIC_PROMPT can be formatted."""
        from prompts.templates import CRITIC_PROMPT
        
        formatted = CRITIC_PROMPT.format(
            proposal="Python is a programming language."
        )
        assert "Python is a programming language." in formatted
        assert "Strengths" in formatted
        assert "Weaknesses" in formatted
