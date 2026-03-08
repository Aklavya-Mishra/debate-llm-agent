"""Debate LLM Agent API - Vercel Serverless Function.

Uses pure HTTP handler approach to avoid Vercel runtime inspection bugs.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# ============================================================================
# Path Setup for Vercel
# ============================================================================

_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


# Lazy imports
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


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""
    
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path in ['/api', '/api/', '/api/health']:
            self._send_json({"status": "healthy", "version": "1.0.0"})
        else:
            self._send_json({"detail": "Not found"}, 404)
    
    def do_POST(self):
        if self.path not in ['/api/debate', '/api/debate/']:
            self._send_json({"detail": "Not found"}, 404)
            return
        
        try:
            _load_agents()
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}
            
            question = data.get('question', '').strip()
            if not question:
                self._send_json({"detail": "Question is required"}, 400)
                return
            
            api_key = data.get('api_key') or os.getenv("OPENAI_API_KEY")
            if not api_key:
                self._send_json({"detail": "API key required"}, 400)
                return
            
            model = data.get('model', 'gpt-4o-mini')
            max_rounds = data.get('max_rounds', 2)
            temperature = data.get('temperature', 0.7)
            base_url = data.get('base_url')
            
            if max_rounds < 1 or max_rounds > 3:
                self._send_json({"detail": "max_rounds must be 1-3"}, 400)
                return
            if temperature < 0 or temperature > 1.5:
                self._send_json({"detail": "temperature must be 0-1.5"}, 400)
                return
            
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
            result = asyncio.run(orchestrator.run_debate(question))
            
            self._send_json(result.model_dump())
            
        except json.JSONDecodeError:
            self._send_json({"detail": "Invalid JSON"}, 400)
        except ValueError as e:
            self._send_json({"detail": str(e)}, 400)
        except Exception as e:
            self._send_json({"detail": f"Debate failed: {str(e)}"}, 500)
