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
        <title>Email Triage - OpenEnv</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-deep: #020617;
                --bg-card: #0f172a;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --accent: #3b82f6;
                --accent-hover: #2563eb;
                --accent-purple: #a855f7;
                --success: #10b981;
                --danger: #ef4444;
                --border: rgba(255, 255, 255, 0.1);
            }
            body {
                margin: 0; padding: 2rem;
                min-height: 100vh;
                background: linear-gradient(135deg, var(--bg-deep), #1e1b4b);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                font-family: 'Outfit', sans-serif;
                color: var(--text-main);
                box-sizing: border-box;
            }
            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: 1fr 350px;
                gap: 2rem;
            }
            .header { grid-column: 1 / -1; display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem;}
            .header h1 { margin: 0; font-size: 2rem; background: linear-gradient(to right, var(--accent-purple), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            
            .card {
                background: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
            
            /* Viewer Section */
            .email-viewer { grid-column: 1; }
            .email-header { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1rem; }
            .email-header p { margin: 0.5rem 0; color: var(--text-muted); font-size: 0.9rem;}
            .email-header h2 { margin: 0; font-size: 1.5rem; }
            .email-body { white-space: pre-wrap; line-height: 1.6; color: #cbd5e1; font-size: 1rem; flex-grow: 1; padding: 1.5rem; background: rgba(0,0,0,0.2); border-radius: 8px;}
            
            /* Action Section */
            .action-panel { grid-column: 2; }
            .panel-title { margin-top: 0; font-size: 1.2rem; color: var(--text-main); border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-bottom: 1rem;}
            
            /* Mood Box UI */
            .mood-box {
                background: rgba(168, 85, 247, 0.1);
                border: 1px solid rgba(168, 85, 247, 0.3);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                font-size: 0.9rem;
            }
            .mood-box strong { color: var(--accent-purple); display: block; margin-bottom: 0.25rem;}
            .mood-box p { margin: 0 0 0.5rem 0; color: #d8b4fe; }
            
            /* Controls */
            label { display: block; margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--text-muted); }
            select, input, textarea {
                width: 100%; box-sizing: border-box; padding: 0.75rem; border-radius: 8px;
                background: rgba(0,0,0,0.3); border: 1px solid var(--border);
                color: white; font-family: inherit; font-size: 1rem; margin-bottom: 1rem;
            }
            select:focus, input:focus { outline: none; border-color: var(--accent); }
            
            button {
                width: 100%; padding: 0.75rem 1rem; border: none; border-radius: 8px;
                font-family: inherit; font-size: 1rem; font-weight: 600; cursor: pointer;
                transition: all 0.2s ease;
            }
            .btn-primary { background: var(--accent); color: white; }
            .btn-primary:hover { background: var(--accent-hover); transform: translateY(-2px); }
            .btn-success { background: var(--success); color: white; }
            .btn-success:hover { background: #059669; transform: translateY(-2px); }
            .btn-danger { background: var(--danger); color: white; }
            .btn-danger:hover { background: #dc2626; transform: translateY(-2px); }
            
            .flex-row { display: flex; gap: 0.5rem; }
            
            /* Feedback Logs */
            .log-box {
                background: #020617; border-radius: 8px; padding: 1rem; font-family: monospace;
                font-size: 0.85rem; color: #10b981; height: 150px; overflow-y: auto;
            }
            .log-error { color: var(--danger); }
            
            /* Status */
            .status-bar { display: flex; gap: 1rem; font-size: 0.9rem; color: var(--text-muted); }
            .status-item span { font-weight: 600; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Triage Agent Console</h1>
                <div class="status-bar">
                    <div class="status-item">Task: <span id="lbl_task">-</span></div>
                    <div class="status-item">Emails Left: <span id="lbl_left">-</span></div>
                    <div class="status-item">Cumulative Reward: <span id="lbl_reward">0.0</span></div>
                </div>
            </div>

            <div class="card email-viewer">
                <div class="email-header">
                    <h2>No Active Session</h2>
                    <p>From: <span>-</span></p>
                    <p>Subject: <span>-</span></p>
                </div>
                
                <div id="mood_container" class="mood-box" style="display: none;">
                    <strong>Active User Profile [Mood Box]</strong>
                    <p id="ui_profile">-</p>
                    <strong>Mood Target Instruction [Mood Box]</strong>
                    <p id="ui_mood">-</p>
                </div>
                
                <div class="email-body">Select a task and hit "Start Episode" to begin evaluating the runtime!</div>
            </div>

            <div class="card action-panel">
                <h3 class="panel-title">Environment Controls</h3>
                <label>Select Task Simulator</label>
                <select id="task_select">
                    <option value="classify_email">Classify Email (Easy)</option>
                    <option value="draft_response">Draft Response (Medium)</option>
                    <option value="full_triage">Full Triage (Hard)</option>
                    <option value="mood_based_triage" selected>Mood Box (Creative) ✨</option>
                </select>
                <button class="btn-primary" onclick="resetEnv()">Start Episode</button>
                <hr style="border:0; border-top: 1px solid var(--border); margin: 1.5rem 0; width: 100%;">
                
                <h3 class="panel-title">Manual Action Dispatch</h3>
                <div id="action_forms" style="display: none;">
                    
                    <div id="form_mood_based_triage" style="display:none;">
                        <label>Target Decision</label>
                        <div class="flex-row">
                            <button class="btn-success" onclick="stepEnv({triage_action: 'accept'})">Accept Match</button>
                            <button class="btn-danger" onclick="stepEnv({triage_action: 'reject'})">Reject Mismatch</button>
                        </div>
                    </div>

                    <div id="form_classify_email" style="display:none;">
                        <label>Priority</label>
                        <select id="inp_priority">
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="urgent">Urgent</option>
                        </select>
                        <label>Category</label>
                        <select id="inp_category">
                            <option value="support">Support</option>
                            <option value="sales">Sales</option>
                            <option value="billing">Billing</option>
                            <option value="technical">Technical</option>
                            <option value="spam">Spam</option>
                        </select>
                        <button class="btn-primary" onclick="submitClassify()">Submit Action</button>
                    </div>

                    <div id="form_draft_response" style="display:none;">
                        <label>Draft</label>
                        <textarea id="inp_response" rows="4" placeholder="Write reply here..."></textarea>
                        <button class="btn-primary" onclick="submitDraft()">Submit Action</button>
                    </div>

                    <div id="form_full_triage" style="display:none;">
                        <label>Routing Department</label>
                        <select id="inp_dept" style="margin-bottom: 0.5rem;">
                            <option value="customer_support">Customer Support</option>
                            <option value="sales">Sales</option>
                            <option value="billing">Billing</option>
                            <option value="engineering">Engineering</option>
                            <option value="spam_filter">Spam Filter</option>
                        </select>
                        <button class="btn-primary" onclick="submitFull()">Submit Action</button>
                        <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.5rem;">(Assumes standard full classification parameters)</p>
                    </div>
                </div>
                
                <h3 class="panel-title" style="margin-top: 1rem;">System Core Logs</h3>
                <div class="log-box" id="sys_logs">
                    > FastAPI Environment initialized on Port 7860...<br>
                </div>
            </div>
        </div>

        <script>
            let currentTask = "";
            let overallScore = 0.0;
            
            function logMsg(msg, isError=false) {
                const box = document.getElementById('sys_logs');
                box.innerHTML += `<div class="${isError?'log-error':''}">&gt; ${msg}</div>`;
                box.scrollTop = box.scrollHeight;
            }

            function updateUI(obs, isDone) {
                if (isDone) {
                    document.querySelector('.email-header h2').innerText = "Simulation Complete!";
                    document.querySelector('.email-body').innerHTML = `<strong>Final Status: Episode Concluded.</strong><br><br>You successfully evaluated the entire test dataset buffer. The final score is reflected in the cumulative reward count.`;
                    document.getElementById('action_forms').style.display = 'none';
                    return;
                }

                document.getElementById('lbl_left').innerText = obs.emails_remaining || "-";
                document.querySelector('.email-header h2').innerText = obs.subject || "No Subject";
                document.querySelector('.email-header p').innerHTML = `From: <span>${obs.sender_name} &lt;${obs.sender}&gt;</span>`;
                document.querySelector('.email-body').innerText = obs.body || "";

                if (currentTask === "mood_based_triage" && obs.user_mood_prompt) {
                    document.getElementById('mood_container').style.display = 'block';
                    document.getElementById('ui_profile').innerText = obs.user_profile;
                    document.getElementById('ui_mood').innerText = obs.user_mood_prompt;
                } else {
                    document.getElementById('mood_container').style.display = 'none';
                }

                document.getElementById('action_forms').style.display = 'block';
                ['mood_based_triage', 'classify_email', 'draft_response', 'full_triage'].forEach(id => {
                    const el = document.getElementById('form_' + id);
                    if (el) el.style.display = 'none';
                });
                const activeForm = document.getElementById('form_' + currentTask);
                if (activeForm) activeForm.style.display = 'block';
            }

            async function resetEnv() {
                const task_type = document.getElementById('task_select').value;
                currentTask = task_type;
                overallScore = 0.0;
                document.getElementById('lbl_task').innerText = task_type;
                document.getElementById('lbl_reward').innerText = "0.0";
                logMsg(`Resetting environment instance for schema: ${task_type}...`);

                try {
                    const res = await fetch('/reset', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({task_type: task_type})
                    });
                    const data = await res.json();
                    
                    logMsg(`Environment provisioned. Loading email batch...`);
                    updateUI(data.observation, false);
                } catch (e) {
                    logMsg(`API Network Error: ${e}`, true);
                }
            }

            async function stepEnv(actionPayload) {
                logMsg(`Dispatching action matrix to grader...`);
                try {
                    const res = await fetch('/step', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({action: actionPayload})
                    });
                    const data = await res.json();
                    
                    let rewardGot = data.reward || 0.0;
                    overallScore += rewardGot;
                    document.getElementById('lbl_reward').innerText = overallScore.toFixed(2);
                    
                    logMsg(`Result Received! Reward: ${rewardGot.toFixed(2)} | System Feedback: ${data.observation?.feedback || "Terminated"}`);
                    
                    updateUI(data.observation, data.done);
                } catch (e) {
                    logMsg(`API Network Error: ${e}`, true);
                }
            }

            function submitClassify() {
                stepEnv({
                    priority: document.getElementById('inp_priority').value,
                    category: document.getElementById('inp_category').value
                });
            }
            function submitDraft() {
                stepEnv({
                    response: document.getElementById('inp_response').value
                });
            }
            function submitFull() {
                stepEnv({
                    priority: document.getElementById('inp_priority').value,
                    category: document.getElementById('inp_category').value,
                    response: document.getElementById('inp_response').value,
                    routing_department: document.getElementById('inp_dept').value
                });
            }
        </script>
    </body>
    </html>
    """

def main():
    """Entry point for direct execution."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
