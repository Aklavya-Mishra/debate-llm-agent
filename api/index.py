"""Vercel serverless function entry point."""

from api.main import app

# Vercel expects a handler named 'handler' or 'app'
handler = app
