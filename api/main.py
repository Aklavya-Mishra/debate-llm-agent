"""Flask application for the Debate LLM Agent.

This API exposes endpoints for running LLM debates where agents
propose, critique, and refine answers collaboratively.
"""

import asyncio
import os
import sys
from pathlib import Path

from flask import Flask, request, jsonify

# ============================================================================
# Path Setup for Vercel
# ============================================================================

_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


# ============================================================================
# Application Setup
# ============================================================================

app = Flask(__name__)


@app.after_request
def after_request(response):
    """Add CORS headers to response."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# Lazy imports to avoid issues at module load time
DebateOrchestrator = None
LLMClient = None
DebateConfig = None


def _load_agents():
    """Lazy load agent modules."""
    global DebateOrchestrator, LLMClient, DebateConfig
    if DebateOrchestrator is None:
        from agents.debate import DebateOrchestrator as DO
        from agents.llm_client import LLMClient as LC
        from agents.models import DebateConfig as DC
        DebateOrchestrator = DO
        LLMClient = LC
        DebateConfig = DC


# ============================================================================
# Endpoints
# ============================================================================

@app.route('/api', methods=['GET'])
def api_root():
    """API root."""
    return jsonify({"status": "healthy", "version": "1.0.0"})


@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check."""
    return jsonify({"status": "healthy", "version": "1.0.0"})


@app.route('/api/debate', methods=['POST', 'OPTIONS'])
def run_debate():
    """Run a debate on the given question."""
    # Handle preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        _load_agents()
        
        data = request.get_json()
        if not data:
            return jsonify({"detail": "Request body required"}), 400
        
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"detail": "Question is required"}), 400
        
        api_key = data.get('api_key') or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({"detail": "API key required"}), 400
        
        model = data.get('model', 'gpt-4o-mini')
        max_rounds = data.get('max_rounds', 2)
        temperature = data.get('temperature', 0.7)
        base_url = data.get('base_url')
        
        # Validate
        if max_rounds < 1 or max_rounds > 3:
            return jsonify({"detail": "max_rounds must be 1-3"}), 400
        if temperature < 0 or temperature > 1.5:
            return jsonify({"detail": "temperature must be 0-1.5"}), 400
        
        llm_client = LLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        
        config = DebateConfig(
            max_rounds=max_rounds,
            temperature=temperature,
            model=model
        )
        
        orchestrator = DebateOrchestrator(llm_client, config)
        
        # Run async code synchronously
        result = asyncio.run(orchestrator.run_debate(question))
        
        # Convert Pydantic model to dict
        return jsonify(result.model_dump())
        
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400
    except Exception as e:
        return jsonify({"detail": f"Debate failed: {str(e)}"}), 500


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=8000)
