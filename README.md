# 🤖 Debate LLM Agent

> An LLM agent that debates itself before answering — showcasing multi-agent reasoning and self-critique loops.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)

**Live Demo:** [debate-llm-agent.vercel.app](https://debate-llm-agent.vercel.app)

## ✨ What is this?

Instead of a normal chatbot giving you a single response, this system uses **two LLM agents** that debate with each other:

```
🎯 Agent A: Proposes an answer
    ↓
🔍 Agent B: Critiques the proposal
    ↓
✨ Agent A: Revises based on feedback
    ↓
✅ Final: Synthesized, refined answer
```

This demonstrates:
- **Agent orchestration** — coordinating multiple AI agents
- **Self-critique loops** — iterative improvement through feedback
- **Reasoning improvement** — better answers through debate

## 🚀 Quick Start

### Deploy to Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Aklavya-Mishra/debate-llm-agent)

1. Click the button above
2. Connect your GitHub account
3. Deploy! (No environment variables needed - users provide their own API key)

### Run Locally

```bash
# Clone the repository
git clone https://github.com/Aklavya-Mishra/debate-llm-agent.git
cd debate-llm-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with Flask dev server
python -m flask --app api.main run --port 8000
```

Then open `http://localhost:8000` in your browser.

## 📁 Project Structure

```
debate-llm-agent/
├── agents/                 # Core debate logic
│   ├── __init__.py
│   ├── debate.py          # DebateOrchestrator - main orchestration
│   ├── llm_client.py      # LLM API wrapper
│   └── models.py          # Pydantic models
├── prompts/               # Prompt templates
│   ├── __init__.py
│   └── templates.py       # Agent prompts
├── api/                   # Python backend
│   ├── __init__.py
│   ├── main.py           # API handler (BaseHTTPRequestHandler)
│   └── index.py          # Vercel entry point
├── public/               # Frontend
│   └── index.html        # Single-page app
├── vercel.json           # Vercel config
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🔧 How It Works

### The Debate Process

1. **Proposal Phase**: Agent A analyzes the question and provides an initial, thoughtful answer
2. **Critique Phase**: Agent B rigorously evaluates the proposal, identifying strengths, weaknesses, and suggesting improvements
3. **Revision Phase**: Agent A incorporates the feedback and produces an improved answer
4. **Synthesis Phase**: A final synthesizer combines the best elements into a refined response

### Why Debate Works

Research shows that LLMs produce better outputs when:
- They're prompted to think step-by-step
- They receive feedback and iterate
- Multiple perspectives are considered

This system automates that process!

## 🛠️ API Reference

### POST `/api/debate`

Run a complete debate on a question.

**Request:**
```json
{
  "question": "What are the pros and cons of microservices?",
  "api_key": "sk-...",
  "model": "gpt-4o-mini",
  "max_rounds": 2,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "question": "What are the pros and cons of microservices?",
  "rounds": [
    {
      "round_number": 1,
      "proposal": "...",
      "critique": "...",
      "revision": "..."
    }
  ],
  "final_answer": "...",
  "confidence": 0.85,
  "reasoning_summary": "Answer refined through 2 debate rounds...",
  "total_tokens_used": 2500
}
```

## 🎨 Features

- **Beautiful UI** — Modern, responsive design with smooth animations
- **BYOK Model** — Users bring their own API key (stored locally, never server-side)
- **Multiple Models** — Support for GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Configurable** — Adjust rounds, temperature, and more
- **Open Source** — MIT licensed, free to use and modify

## 💡 Use Cases

- **Complex Questions** — Get more nuanced answers through debate
- **Decision Making** — Explore pros/cons systematically
- **Learning** — See how AI reasons through problems
- **Research** — Understand multi-agent architectures

## 🤝 Compatible Providers

Works with any OpenAI-compatible API:

| Provider | Base URL | Notes |
|----------|----------|-------|
| OpenAI | (default) | Full support |
| Groq | `https://api.groq.com/openai/v1` | Fast inference |
| Together | `https://api.together.xyz/v1` | Many models |
| Ollama | `http://localhost:11434/v1` | Local LLMs |

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (UI)                       │
│                   public/index.html                      │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/SSE
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Python Backend                        │
│                     api/main.py                          │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 DebateOrchestrator                       │
│                  agents/debate.py                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │ Proposer │───▶│  Critic  │───▶│   Synthesizer    │   │
│  │ (Agent A)│    │(Agent B) │    │                  │   │
│  └──────────┘    └──────────┘    └──────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     LLM Client                           │
│                 agents/llm_client.py                     │
│            (OpenAI API / Compatible)                     │
└─────────────────────────────────────────────────────────┘
```

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Format
ruff format .
```

## 📈 Future Ideas

- [ ] Add streaming for individual agent responses
- [ ] Support for image inputs
- [ ] Debate history export
- [ ] Custom prompt templates
- [ ] More LLM providers
- [ ] Evaluation metrics

## 📜 License

MIT License — feel free to use this for your portfolio, projects, or anything else!

## 🙏 Acknowledgments

Inspired by research on:
- [Debate helps language models](https://arxiv.org/abs/2311.08401)
- [Self-Refine](https://arxiv.org/abs/2303.17651)
- [Constitutional AI](https://arxiv.org/abs/2212.08073)

---

<p align="center">
  Made with ❤️ for the AI community
</p>
