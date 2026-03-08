"""FastAPI application for the Debate LLM Agent.

This API exposes endpoints for running LLM debates where agents
propose, critique, and refine answers collaboratively.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ============================================================================
# Path Setup for Vercel
# ============================================================================

_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Lazy imports to avoid issues at module load time
DebateOrchestrator = None
LLMClient = None
DebateConfig = None
DebateResult = None


def _load_agents():
    """Lazy load agent modules."""
    global DebateOrchestrator, LLMClient, DebateConfig, DebateResult
    if DebateOrchestrator is None:
        from agents.debate import DebateOrchestrator as DO
        from agents.llm_client import LLMClient as LC
        from agents.models import DebateConfig as DC, DebateResult as DR
        DebateOrchestrator = DO
        LLMClient = LC
        DebateConfig = DC
        DebateResult = DR


# ============================================================================
# Request/Response Models
# ============================================================================

class DebateRequest(BaseModel):
    """Request body for debate endpoint."""
    question: str = Field(..., min_length=1, max_length=2000)
    api_key: Optional[str] = Field(None, description="OpenAI API key")
    base_url: Optional[str] = Field(None, description="Custom API base URL")
    model: str = Field("gpt-4o-mini", description="Model to use")
    max_rounds: int = Field(2, ge=1, le=3, description="Number of debate rounds")
    temperature: float = Field(0.7, ge=0.0, le=1.5)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# ============================================================================
# Application Setup
# ============================================================================

app = FastAPI(
    title="Debate LLM Agent",
    description="An LLM agent that debates itself before answering",
    version="1.0.0",
)

# CORS - allow all for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/api")
async def api_root():
    """API root."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/health")
async def api_health():
    """Health check."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/debate")
async def run_debate(request: DebateRequest):
    """Run a debate on the given question."""
    try:
        _load_agents()
        
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="API key required."
            )
        
        llm_client = LLMClient(
            api_key=api_key,
            base_url=request.base_url,
            model=request.model
        )
        
        config = DebateConfig(
            max_rounds=request.max_rounds,
            temperature=request.temperature,
            model=request.model
        )
        
        orchestrator = DebateOrchestrator(llm_client, config)
        result = await orchestrator.run_debate(request.question)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debate failed: {str(e)}")
