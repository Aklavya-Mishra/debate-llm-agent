"""Prompt templates for the debate agents.

These prompts are designed to elicit concise, high-quality reasoning.
"""

PROPOSER_PROMPT = """You are Agent A. Give a clear, concise answer.

Rules:
- Be direct and specific
- Use bullet points for lists
- Keep response under 200 words

{revision_context}

QUESTION: {question}

Your {answer_type}:"""


CRITIC_PROMPT = """You are Agent B. Briefly critique this answer.

PROPOSAL:
{proposal}

Provide in 100 words or less:
- Key strengths (1-2 points)
- Key weaknesses (1-2 points)  
- One specific improvement
- Confidence: X%"""


SYNTHESIZER_PROMPT = """Synthesize the best answer from this debate.

QUESTION: {question}

DEBATE:
{debate_history}

Provide a clear, concise final answer (under 250 words). Do not reference the debate.

FINAL ANSWER:"""


REVISION_CONTEXT_TEMPLATE = """
Previous: {previous_proposal}

Feedback: {critique}

Improve based on feedback.
"""
