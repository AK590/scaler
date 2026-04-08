"""
FastAPI application for the Email Triage Environment.

This is the root-level server/app.py expected by the openenv validator.

Usage:
    uvicorn server.app:app --host 0.0.0.0 --port 8000
"""

import sys
import os

# Ensure the parent directory is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_triage_env.server.app import app  # noqa: F401


def main():
    """Entry point for direct execution."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
