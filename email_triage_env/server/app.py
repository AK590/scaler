"""
FastAPI application for the Email Triage Environment.

Exposes the EmailTriageEnvironment over HTTP and WebSocket endpoints,
compatible with OpenEnv EnvClient.

Usage:
    uvicorn server.app:app --host 0.0.0.0 --port 8000
"""

try:
    from openenv.core.env_server.http_server import create_app
    from .email_triage_environment import EmailTriageEnvironment
except ImportError:
    from openenv.core.env_server.http_server import create_app
    from server.email_triage_environment import EmailTriageEnvironment

try:
    from ..models import EmailTriageAction, EmailTriageObservation
except ImportError:
    import sys
    import os
    # Add parent to path for standalone mode
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import EmailTriageAction, EmailTriageObservation

from openenv.core.env_server.types import Observation

# Create the FastAPI app using OpenEnv's create_app helper
app = create_app(
    EmailTriageEnvironment,
    EmailTriageAction,
    EmailTriageObservation,
    env_name="email_triage_env",
)


def main():
    """Entry point for direct execution."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
