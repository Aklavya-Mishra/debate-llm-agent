"""Core debate orchestration logic.

This module implements the multi-agent debate pattern:
1. Agent A proposes an initial answer
2. Agent B critiques the proposal
3. Agent A revises based on critique
4. (Optional) Repeat for multiple rounds
5. Synthesize final answer
"""

import re
from typing import AsyncIterator, Optional

from .llm_client import LLMClient
from .models import DebateConfig, DebateResult, DebateRound
from prompts.templates import (
    PROPOSER_PROMPT,
    CRITIC_PROMPT,
    SYNTHESIZER_PROMPT,
    REVISION_CONTEXT_TEMPLATE,
)


class DebateOrchestrator:
    """Orchestrates the debate between agents."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        config: Optional[DebateConfig] = None
    ):
        self.llm = llm_client
        self.config = config or DebateConfig()
        self.total_tokens = 0
    
    async def run_debate(self, question: str) -> DebateResult:
        """Run the complete debate process.
        
        Args:
            question: The user's question to debate
            
        Returns:
            DebateResult with the final answer and debate history
        """
        rounds: list[DebateRound] = []
        current_proposal = ""
        
        for round_num in range(1, self.config.max_rounds + 1):
            # Step 1: Propose (or revise)
            if round_num == 1:
                proposal = await self._propose(question)
            else:
                proposal = await self._revise(
                    question,
                    current_proposal,
                    rounds[-1].critique
                )
            
            current_proposal = proposal
            
            # Step 2: Critique
            critique = await self._critique(proposal)
            
            # Step 3: Revise based on critique
            revision = await self._revise(question, proposal, critique)
            
            rounds.append(DebateRound(
                round_number=round_num,
                proposal=proposal,
                critique=critique,
                revision=revision
            ))
            
            current_proposal = revision
        
        # Step 4: Final synthesis
        final_answer = await self._synthesize(question, rounds)
        confidence = self._extract_confidence(rounds)
        
        return DebateResult(
            question=question,
            rounds=rounds,
            final_answer=final_answer,
            confidence=confidence,
            reasoning_summary=self._generate_summary(rounds),
            total_tokens_used=self.total_tokens
        )
    
    async def run_debate_stream(
        self,
        question: str
    ) -> AsyncIterator[dict]:
        """Run debate with streaming updates.
        
        Yields status updates and content as the debate progresses.
        """
        rounds: list[DebateRound] = []
        current_proposal = ""
        
        for round_num in range(1, self.config.max_rounds + 1):
            # Proposal phase
            yield {"type": "status", "phase": "proposing", "round": round_num}
            
            if round_num == 1:
                proposal = await self._propose(question)
            else:
                proposal = await self._revise(
                    question,
                    current_proposal,
                    rounds[-1].critique
                )
            
            yield {"type": "proposal", "content": proposal, "round": round_num}
            current_proposal = proposal
            
            # Critique phase
            yield {"type": "status", "phase": "critiquing", "round": round_num}
            critique = await self._critique(proposal)
            yield {"type": "critique", "content": critique, "round": round_num}
            
            # Revision phase
            yield {"type": "status", "phase": "revising", "round": round_num}
            revision = await self._revise(question, proposal, critique)
            yield {"type": "revision", "content": revision, "round": round_num}
            
            rounds.append(DebateRound(
                round_number=round_num,
                proposal=proposal,
                critique=critique,
                revision=revision
            ))
            
            current_proposal = revision
        
        # Synthesis phase
        yield {"type": "status", "phase": "synthesizing", "round": 0}
        final_answer = await self._synthesize(question, rounds)
        
        yield {
            "type": "final",
            "content": final_answer,
            "confidence": self._extract_confidence(rounds),
            "tokens_used": self.total_tokens
        }
    
    async def _propose(self, question: str) -> str:
        """Generate initial proposal."""
        prompt = PROPOSER_PROMPT.format(
            question=question,
            revision_context="",
            answer_type="initial answer"
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            temperature=self.config.temperature
        )
        self.total_tokens += response.tokens_used
        return response.content
    
    async def _critique(self, proposal: str) -> str:
        """Generate critique of the proposal."""
        prompt = CRITIC_PROMPT.format(proposal=proposal)
        
        response = await self.llm.generate(
            prompt=prompt,
            temperature=self.config.temperature
        )
        self.total_tokens += response.tokens_used
        return response.content
    
    async def _revise(
        self,
        question: str,
        proposal: str,
        critique: str
    ) -> str:
        """Revise proposal based on critique."""
        revision_context = REVISION_CONTEXT_TEMPLATE.format(
            previous_proposal=proposal,
            critique=critique
        )
        
        prompt = PROPOSER_PROMPT.format(
            question=question,
            revision_context=revision_context,
            answer_type="improved answer"
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            temperature=self.config.temperature
        )
        self.total_tokens += response.tokens_used
        return response.content
    
    async def _synthesize(
        self,
        question: str,
        rounds: list[DebateRound]
    ) -> str:
        """Synthesize final answer from debate history."""
        debate_history = self._format_debate_history(rounds)
        
        prompt = SYNTHESIZER_PROMPT.format(
            question=question,
            debate_history=debate_history
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.5  # Lower temp for final synthesis
        )
        self.total_tokens += response.tokens_used
        return response.content
    
    def _format_debate_history(self, rounds: list[DebateRound]) -> str:
        """Format debate rounds into readable history."""
        history_parts = []
        
        for r in rounds:
            history_parts.append(f"""
--- Round {r.round_number} ---

PROPOSAL:
{r.proposal}

CRITIQUE:
{r.critique}

REVISION:
{r.revision}
""")
        
        return "\n".join(history_parts)
    
    def _extract_confidence(self, rounds: list[DebateRound]) -> float:
        """Extract confidence score from critique."""
        if not rounds:
            return 0.5
        
        last_critique = rounds[-1].critique
        
        # Look for confidence score pattern
        match = re.search(r"Confidence Score[:\s]*(\d+)%?", last_critique, re.IGNORECASE)
        if match:
            return min(int(match.group(1)) / 100, 1.0)
        
        return 0.75  # Default confidence
    
    def _generate_summary(self, rounds: list[DebateRound]) -> str:
        """Generate a brief summary of the reasoning process."""
        if not rounds:
            return "No debate rounds completed."
        
        total_rounds = len(rounds)
        return (
            f"Answer refined through {total_rounds} debate round(s). "
            f"Each round involved proposal, critique, and revision to improve quality."
        )
