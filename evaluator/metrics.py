"""Metrics and evaluation for debate quality.

This module provides tools to evaluate the quality of debates,
including measuring improvement across rounds and critique effectiveness.
"""

from typing import Optional
from pydantic import BaseModel, Field

from agents.models import DebateResult, DebateRound


class EvaluationResult(BaseModel):
    """Results from evaluating a debate."""
    
    improvement_score: float = Field(
        ge=0.0, le=1.0,
        description="How much the answer improved through debate"
    )
    critique_quality: float = Field(
        ge=0.0, le=1.0,
        description="Quality of critiques provided"
    )
    revision_effectiveness: float = Field(
        ge=0.0, le=1.0,
        description="How well revisions addressed critiques"
    )
    overall_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall debate quality score"
    )
    insights: list[str] = Field(
        default_factory=list,
        description="Key insights from the evaluation"
    )


class DebateEvaluator:
    """Evaluates the quality and effectiveness of debates.
    
    This can be used to:
    - Measure how much answers improve through iteration
    - Assess critique quality
    - Track reasoning improvements
    """
    
    def __init__(self):
        self._weights = {
            "improvement": 0.4,
            "critique": 0.3,
            "revision": 0.3
        }
    
    def evaluate(self, result: DebateResult) -> EvaluationResult:
        """Evaluate a completed debate.
        
        Args:
            result: The debate result to evaluate
            
        Returns:
            EvaluationResult with scores and insights
        """
        if not result.rounds:
            return EvaluationResult(
                improvement_score=0.0,
                critique_quality=0.0,
                revision_effectiveness=0.0,
                overall_score=0.0,
                insights=["No debate rounds to evaluate"]
            )
        
        # Calculate individual metrics
        improvement = self._measure_improvement(result.rounds)
        critique_quality = self._measure_critique_quality(result.rounds)
        revision_effectiveness = self._measure_revision_effectiveness(result.rounds)
        
        # Calculate weighted overall score
        overall = (
            improvement * self._weights["improvement"] +
            critique_quality * self._weights["critique"] +
            revision_effectiveness * self._weights["revision"]
        )
        
        # Generate insights
        insights = self._generate_insights(
            result, improvement, critique_quality, revision_effectiveness
        )
        
        return EvaluationResult(
            improvement_score=improvement,
            critique_quality=critique_quality,
            revision_effectiveness=revision_effectiveness,
            overall_score=overall,
            insights=insights
        )
    
    def _measure_improvement(self, rounds: list[DebateRound]) -> float:
        """Measure how much the answer improved across rounds.
        
        Uses heuristics like:
        - Length changes (more detail often = improvement)
        - Structure (lists, headers = better organization)
        - Addressed critique points
        """
        if len(rounds) < 1:
            return 0.0
        
        # Compare first proposal to final revision
        first_proposal = rounds[0].proposal
        final_revision = rounds[-1].revision
        
        # Length ratio (capped improvement)
        len_ratio = len(final_revision) / max(len(first_proposal), 1)
        length_score = min(len_ratio, 1.5) / 1.5  # Normalize to 0-1
        
        # Structure improvements (simple heuristics)
        structure_indicators = ["**", "- ", "1.", "2.", ":"]
        first_structure = sum(1 for i in structure_indicators if i in first_proposal)
        final_structure = sum(1 for i in structure_indicators if i in final_revision)
        structure_score = min((final_structure - first_structure + 3) / 6, 1.0)
        
        return (length_score * 0.4 + structure_score * 0.6)
    
    def _measure_critique_quality(self, rounds: list[DebateRound]) -> float:
        """Measure the quality of critiques.
        
        Good critiques:
        - Identify specific strengths and weaknesses
        - Provide actionable suggestions
        - Include confidence assessments
        """
        if not rounds:
            return 0.0
        
        total_score = 0.0
        
        for round in rounds:
            critique = round.critique.lower()
            
            # Check for structured feedback
            has_strengths = "strength" in critique
            has_weaknesses = "weakness" in critique or "issue" in critique
            has_suggestions = "suggest" in critique or "improve" in critique
            has_confidence = "confidence" in critique or "%" in critique
            
            round_score = (
                (0.25 if has_strengths else 0) +
                (0.25 if has_weaknesses else 0) +
                (0.25 if has_suggestions else 0) +
                (0.25 if has_confidence else 0)
            )
            
            total_score += round_score
        
        return total_score / len(rounds)
    
    def _measure_revision_effectiveness(self, rounds: list[DebateRound]) -> float:
        """Measure how well revisions address critiques.
        
        Effective revisions:
        - Show clear changes from the original
        - Address critique points
        - Maintain original strengths
        """
        if not rounds:
            return 0.0
        
        total_score = 0.0
        
        for round in rounds:
            # Check if revision differs significantly from proposal
            proposal_words = set(round.proposal.lower().split())
            revision_words = set(round.revision.lower().split())
            
            # Calculate Jaccard similarity (lower = more changes)
            intersection = len(proposal_words & revision_words)
            union = len(proposal_words | revision_words)
            similarity = intersection / max(union, 1)
            
            # We want some changes but not complete rewrites
            # Sweet spot is around 0.5-0.7 similarity
            if similarity > 0.9:
                change_score = 0.3  # Too similar
            elif similarity < 0.3:
                change_score = 0.5  # Maybe too different
            else:
                change_score = 1.0  # Good balance
            
            # Check if revision is longer (usually means more detail)
            length_improvement = len(round.revision) > len(round.proposal)
            length_score = 0.8 if length_improvement else 0.5
            
            total_score += (change_score * 0.6 + length_score * 0.4)
        
        return total_score / len(rounds)
    
    def _generate_insights(
        self,
        result: DebateResult,
        improvement: float,
        critique_quality: float,
        revision_effectiveness: float
    ) -> list[str]:
        """Generate human-readable insights from the evaluation."""
        insights = []
        
        # Improvement insights
        if improvement > 0.7:
            insights.append("Strong improvement through debate rounds")
        elif improvement < 0.4:
            insights.append("Limited improvement - consider more rounds")
        
        # Critique insights
        if critique_quality > 0.7:
            insights.append("Critiques were structured and actionable")
        elif critique_quality < 0.4:
            insights.append("Critiques could be more specific")
        
        # Revision insights
        if revision_effectiveness > 0.7:
            insights.append("Revisions effectively addressed feedback")
        elif revision_effectiveness < 0.4:
            insights.append("Revisions showed minimal changes")
        
        # Overall assessment
        overall = (improvement + critique_quality + revision_effectiveness) / 3
        if overall > 0.7:
            insights.append(f"High-quality debate (confidence: {result.confidence:.0%})")
        elif overall > 0.5:
            insights.append("Moderate debate quality - room for improvement")
        else:
            insights.append("Consider adjusting prompts or increasing rounds")
        
        return insights


def quick_evaluate(result: DebateResult) -> dict:
    """Quick evaluation function for simple use cases.
    
    Args:
        result: The debate result to evaluate
        
    Returns:
        Dictionary with key metrics
    """
    evaluator = DebateEvaluator()
    evaluation = evaluator.evaluate(result)
    
    return {
        "overall": round(evaluation.overall_score, 2),
        "improvement": round(evaluation.improvement_score, 2),
        "critique_quality": round(evaluation.critique_quality, 2),
        "insights": evaluation.insights
    }
