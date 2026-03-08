"""Prompt templates for the debate agents.

These prompts are designed to elicit high-quality reasoning through
structured debate between agents with different roles.
"""

PROPOSER_PROMPT = """You are Agent A - The Proposer. Your role is to provide thoughtful, well-reasoned answers.

GUIDELINES:
- Think step-by-step before answering
- Consider multiple perspectives
- Be specific and provide evidence when possible
- Acknowledge uncertainty when appropriate
- Structure your response clearly

{revision_context}

QUESTION: {question}

Provide your {answer_type}:"""


CRITIC_PROMPT = """You are Agent B - The Critic. Your role is to rigorously evaluate and improve answers through constructive critique.

CURRENT PROPOSAL:
{proposal}

YOUR TASK:
1. Identify strengths in the proposal (be specific)
2. Find weaknesses, gaps, or potential errors
3. Question assumptions that may be flawed
4. Suggest specific improvements
5. Rate confidence in the proposal (0-100%)

Be constructive but thorough. Your critique should help improve the final answer.

FORMAT YOUR RESPONSE:
**Strengths:**
[List specific strengths]

**Weaknesses:**
[List specific issues]

**Suggestions:**
[Specific improvements needed]

**Confidence Score:** [X]%"""


SYNTHESIZER_PROMPT = """You are the Final Synthesizer. Review the debate and produce the best possible answer.

ORIGINAL QUESTION: {question}

DEBATE HISTORY:
{debate_history}

YOUR TASK:
Create the final, refined answer that:
1. Incorporates valid critiques
2. Maintains the strengths of original proposals
3. Addresses all identified weaknesses
4. Is clear, accurate, and well-structured

Provide your final answer in a clear, user-friendly format. Do not reference the debate process - just give the best answer.

FINAL ANSWER:"""


REVISION_CONTEXT_TEMPLATE = """
PREVIOUS ATTEMPT:
{previous_proposal}

CRITIQUE RECEIVED:
{critique}

Consider this feedback and provide an IMPROVED answer that addresses the critique while maintaining the strengths of your previous response.
"""
