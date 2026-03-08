"""Tests for the evaluator module."""

import pytest
from agents.models import DebateResult, DebateRound
from evaluator.metrics import DebateEvaluator, EvaluationResult, quick_evaluate


class TestDebateEvaluator:
    """Test the debate evaluator."""
    
    def test_evaluate_empty_result(self):
        """Test evaluation of result with no rounds."""
        evaluator = DebateEvaluator()
        result = DebateResult(
            question="Test",
            final_answer="Answer",
            confidence=0.5,
            reasoning_summary="No rounds"
        )
        
        evaluation = evaluator.evaluate(result)
        assert evaluation.overall_score == 0.0
        assert "No debate rounds" in evaluation.insights[0]
    
    def test_evaluate_single_round(self):
        """Test evaluation of result with one round."""
        evaluator = DebateEvaluator()
        
        result = DebateResult(
            question="What is AI?",
            rounds=[
                DebateRound(
                    round_number=1,
                    proposal="AI is artificial intelligence.",
                    critique="**Strengths:** Clear definition. **Weaknesses:** Too brief. **Suggestions:** Add examples. **Confidence:** 60%",
                    revision="AI is artificial intelligence - the simulation of human intelligence by machines. Examples include chatbots and self-driving cars."
                )
            ],
            final_answer="AI is the simulation of human intelligence by machines.",
            confidence=0.75,
            reasoning_summary="One round completed"
        )
        
        evaluation = evaluator.evaluate(result)
        
        assert evaluation.overall_score > 0
        assert evaluation.critique_quality > 0.5  # Has all expected elements
        assert isinstance(evaluation.insights, list)
    
    def test_critique_quality_scoring(self):
        """Test that critique quality scoring works correctly."""
        evaluator = DebateEvaluator()
        
        # High quality critique
        good_rounds = [
            DebateRound(
                round_number=1,
                proposal="Test proposal",
                critique="**Strengths:** Good. **Weaknesses:** Issues found. **Suggestions:** Improve X. **Confidence:** 80%",
                revision="Revised proposal"
            )
        ]
        
        result = DebateResult(
            question="Test",
            rounds=good_rounds,
            final_answer="Final",
            confidence=0.8,
            reasoning_summary="Test"
        )
        
        evaluation = evaluator.evaluate(result)
        assert evaluation.critique_quality == 1.0  # All elements present


class TestQuickEvaluate:
    """Test the quick_evaluate function."""
    
    def test_quick_evaluate_returns_dict(self):
        """Test that quick_evaluate returns expected format."""
        result = DebateResult(
            question="Test",
            final_answer="Answer",
            confidence=0.7,
            reasoning_summary="Summary"
        )
        
        output = quick_evaluate(result)
        
        assert isinstance(output, dict)
        assert "overall" in output
        assert "improvement" in output
        assert "insights" in output
