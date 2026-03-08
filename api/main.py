"""FastAPI application for the Debate LLM Agent.

This API exposes endpoints for running LLM debates where agents
propose, critique, and refine answers collaboratively.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Ensure the project root is in the path for imports (Vercel serverless compatibility)
# This must happen before importing local modules
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent
_agents_path = _project_root / "agents"

# Add project root to path if agents directory exists there
if _agents_path.exists() and str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

try:
    from agents.debate import DebateOrchestrator
    from agents.llm_client import LLMClient
    from agents.models import DebateConfig, DebateResult
except ImportError as e:
    # Fallback: try importing from current working directory
    import importlib.util
    raise ImportError(
        f"Failed to import agents module. "
        f"Project root: {_project_root}, "
        f"Agents path exists: {_agents_path.exists()}, "
        f"sys.path: {sys.path[:3]}, "
        f"Original error: {e}"
    )


# ============================================================================
# Request/Response Models
# ============================================================================

class DebateRequest(BaseModel):
    """Request body for debate endpoint."""
    question: str = Field(..., min_length=1, max_length=2000)
    api_key: Optional[str] = Field(None, description="OpenAI API key (uses env var if not provided)")
    base_url: Optional[str] = Field(None, description="Custom API base URL for compatible providers")
    model: str = Field("gpt-4o-mini", description="Model to use")
    max_rounds: int = Field(2, ge=1, le=3, description="Number of debate rounds")
    temperature: float = Field(0.7, ge=0.0, le=1.5)
    stream: bool = Field(False, description="Enable streaming response")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# ============================================================================
# Application Setup
# ============================================================================

app = FastAPI(
    title="Debate LLM Agent",
    description="An LLM agent that debates itself before answering - showcasing multi-agent reasoning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
# In production, requests come from the same origin (Vercel serves both API + frontend)
# These origins are allowed for local development and specific external access
ALLOWED_ORIGINS = [
    "http://localhost:8000",      # Local development
    "http://127.0.0.1:8000",      # Local development (alternative)
    "http://localhost:3000",      # If running frontend separately
]

# Add production Vercel domain from environment variable
VERCEL_URL = os.getenv("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_ORIGINS.append(f"https://{VERCEL_URL}")

# Add custom domain if configured
CUSTOM_DOMAIN = os.getenv("CORS_ALLOWED_ORIGIN")
if CUSTOM_DOMAIN:
    ALLOWED_ORIGINS.append(CUSTOM_DOMAIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # No cookies/auth headers needed
    allow_methods=["GET", "POST", "OPTIONS"],  # Only methods we use
    allow_headers=["Content-Type"],  # Only headers we need
)


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/api")
async def api_root():
    """API root - returns health info."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """API health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@app.post("/api/debate", response_model=DebateResult)
async def run_debate(request: DebateRequest):
    """Run a debate on the given question.
    
    The debate process:
    1. Agent A proposes an initial answer
    2. Agent B critiques the proposal
    3. Agent A revises based on critique
    4. Repeat for specified rounds
    5. Synthesize final answer
    
    Returns the complete debate history and final refined answer.
    """
    try:
        # Initialize LLM client
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="API key required. Provide in request or set OPENAI_API_KEY environment variable."
            )
        
        llm_client = LLMClient(
            api_key=api_key,
            base_url=request.base_url,
            model=request.model
        )
        
        # Configure and run debate
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


@app.post("/api/debate/stream")
async def run_debate_stream(request: DebateRequest):
    """Run a debate with streaming updates.
    
    Returns Server-Sent Events with real-time progress.
    """
    import json
    
    async def generate():
        try:
            api_key = request.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                yield f"data: {json.dumps({'type': 'error', 'content': 'API key required'})}\n\n"
                return
            
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
            
            async for update in orchestrator.run_debate_stream(request.question):
                yield f"data: {json.dumps(update)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


# ============================================================================
# Vercel Handler
# ============================================================================

# For Vercel serverless deployment
handler = app
