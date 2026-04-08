# 📧 Email Triage Agent — OpenEnv Environment

An AI agent environment that simulates real-world **email triage** — classifying, responding to, and routing incoming emails. Built on the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) framework.

## 🎯 Overview

Every business handles email triage daily: reading incoming messages, determining urgency, categorizing them, drafting appropriate responses, and routing them to the right department. This environment lets AI agents practice and learn this critical skill.

The agent receives emails one at a time and must perform actions appropriate to the task difficulty level. Grading is deterministic and rubric-based, providing meaningful partial-progress reward signals.

## 📋 Tasks

| Task | Difficulty | Description | Max Score |
|------|-----------|-------------|-----------|
| `classify_email` | 🟢 Easy | Classify email priority and category | 1.0 |
| `draft_response` | 🟡 Medium | Draft a professional response | 1.0 |
| `full_triage` | 🔴 Hard | Classify + respond + route the email | 1.0 |
| `mood_based_triage` | ✨ Creative | "Mood Box" dynamic filtering (Hackathon) | 1.0 |

Each task consists of **5 emails per episode**. The final score is the **average reward** across all emails, normalized to [0.0, 1.0].

### ✨ The "Mood Box" Feature (Hackathon Production-Ready)
To align with creative user-targeted approaches, we introduced the **Mood Box**. By supplying a generic user profile (Resume) and a situational "mood prompt" (e.g., *“3rd-year student looking for internships. Block pure promotional Unstop challenges or Telegram groups”*), the agent dynamically regulates incoming marketplace traffic.
- **Action**: The agent uses the instruction to choose a `triage_action` (`"accept"` / `"reject"`).
- **Graceful Control**: Successfully passes Internshala / TopHire tech opportunities while blocking purely irrelevant Unstop spam or crypto telegrams—protecting your cognitive palette!

## 🔧 Action Space

```python
class EmailTriageAction:
    priority: str           # "low" | "medium" | "high" | "urgent"
    category: str           # "support" | "sales" | "billing" | "technical" | "spam"
    response: str           # Draft response text
    routing_department: str # "customer_support" | "sales" | "billing" | "engineering" | "spam_filter"
    triage_action: str      # "accept" | "reject" (for mood_based_triage)
```

Which fields are relevant depends on the task:
- **classify_email**: `priority`, `category`
- **draft_response**: `response`
- **full_triage**: All fields
- **mood_based_triage**: `triage_action`

## 👁️ Observation Space

```python
class EmailTriageObservation:
    email_id: str           # Unique email identifier
    subject: str            # Email subject line
    body: str               # Email body text
    sender: str             # Sender email address
    sender_name: str        # Sender display name
    task_type: str           # Current task type
    emails_remaining: int   # Emails left in episode
    feedback: str           # Grader feedback from last action
    done: bool              # Episode finished?
    reward: float           # Reward from last action [0.0, 1.0]
    user_profile: str       # Mood Box Resume context (for mood_based_triage)
    user_mood_prompt: str   # Mood Box Filtering instructions (for mood_based_triage)
```

## 📊 Reward Function

### classify_email (Easy)
- **0.5** for correct priority (0.2 for one-level-off)
- **0.5** for correct category
- Total: 0.0 – 1.0

### draft_response (Medium)
Four rubric dimensions (0.25 each):
1. Addresses sender by name
2. Acknowledges the topic/issue
3. Provides actionable next steps
4. Professional tone & appropriate length

### full_triage (Hard)
Composite scoring:
- **0.25** for correct priority
- **0.25** for correct category
- **0.25** for response quality (rubric)
- **0.25** for correct routing department

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)

### Local Development

```bash
# Clone the repo
git clone <your-repo-url>
cd scaler

# Install dependencies
pip install -e .

# Start the server locally
uvicorn email_triage_env.server.app:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build the image
docker build -t email-triage-env .

# Run the container
docker run -p 8000:8000 email-triage-env
```

### Run Inference

```bash
# Set required environment variables
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your-hf-token"

# If using Docker:
export IMAGE_NAME="email-triage-env"

# If connecting to a running server:
export ENV_BASE_URL="http://localhost:8000"

# Run
python inference.py
```

## 🏗️ Architecture

```
email_triage_env/
├── __init__.py              # Package exports
├── models.py                # Typed Action/Observation/State (Pydantic)
├── client.py                # EnvClient subclass
├── graders.py               # Deterministic rubric-based grading
├── email_data.py            # 15 realistic emails with ground truth
└── server/
    ├── __init__.py
    ├── email_triage_environment.py  # Core Environment logic
    └── app.py               # FastAPI application
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset environment, returns first email |
| `/step` | POST | Submit action, get next email + reward |
| `/state` | GET | Get current episode state |
| `/health` | GET | Health check |
| `/schema` | GET | Action/Observation JSON schemas |
| `/ws` | WebSocket | Persistent session connection |

## 📝 Example Usage

### Python (Async)

```python
from email_triage_env import EmailTriageEnv, EmailTriageAction

async with EmailTriageEnv(base_url="http://localhost:8000") as env:
    result = await env.reset(task_type="classify_email")

    while not result.done:
        action = EmailTriageAction(
            priority="high",
            category="support"
        )
        result = await env.step(action)
        print(f"Reward: {result.reward}, Feedback: {result.observation.feedback}")
```

### cURL

```bash
# Reset
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_type": "classify_email"}'

# Step
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"priority": "high", "category": "support"}}'
```

## 📜 License

BSD 3-Clause License
