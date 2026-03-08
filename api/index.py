"""Vercel serverless function entry point."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and expose the FastAPI app
from api.main import app

# Vercel looks for 'app' or 'handler'
handler = app
