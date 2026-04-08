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
from fastapi.responses import HTMLResponse

# Create the FastAPI app using OpenEnv's create_app helper
app = create_app(
    EmailTriageEnvironment,
    EmailTriageAction,
    EmailTriageObservation,
    env_name="email_triage_env",
)

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Triage - MoodBox</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #0f172a, #1e1b4b, #020617);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                font-family: 'Outfit', sans-serif;
                color: #f8fafc;
            }
            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 24px;
                padding: 4rem 3rem;
                text-align: center;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                max-width: 500px;
                transition: transform 0.3s ease;
            }
            .glass-card:hover {
                transform: translateY(-5px);
            }
            .status-badge {
                display: inline-flex;
                align-items: center;
                padding: 8px 16px;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 99px;
                color: #10b981;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 24px;
            }
            .pulse {
                width: 8px;
                height: 8px;
                background-color: #10b981;
                border-radius: 50%;
                margin-right: 8px;
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
                animation: pulsing 2s infinite;
            }
            @keyframes pulsing {
                0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
                100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }
            h1 {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(to right, #a855f7, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 16px;
            }
            p {
                color: #94a3b8;
                line-height: 1.6;
                margin-bottom: 32px;
                font-weight: 300;
            }
            .endpoints {
                text-align: left;
                background: rgba(0, 0, 0, 0.2);
                padding: 16px;
                border-radius: 12px;
            }
            .endpoints h3 {
                margin-top: 0;
                font-size: 14px;
                color: #cbd5e1;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .route {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-family: monospace;
                font-size: 14px;
                color: #a855f7;
            }
            .route span { color: #64748b; }
        </style>
    </head>
    <body>
        <div class="glass-card">
            <div class="status-badge">
                <div class="pulse"></div>
                MoodBox Server Online
            </div>
            <h1>Email Triage Agent</h1>
            <p>The OpenEnv simulation is flawlessly compiled and actively listening for HTTP traffic. This API serves strictly as a headless backend for hackathon graders.</p>
            <div class="endpoints">
                <h3>Core Routes Active</h3>
                <div class="route">GET <span>/info</span></div>
                <div class="route">POST <span>/reset</span></div>
                <div class="route">POST <span>/step</span></div>
            </div>
        </div>
    </body>
    </html>
    """

def main():
    """Entry point for direct execution."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
