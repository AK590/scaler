"""
Inference Script for Email Triage Environment
==============================================

MANDATORY VARIABLES:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    IMAGE_NAME     The Docker image name (if using from_docker_image).

STDOUT FORMAT:
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import asyncio
import os
import textwrap
from typing import Any, Dict, List, Optional

from openai import OpenAI

from email_triage_env import EmailTriageAction, EmailTriageEnv

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

BENCHMARK = "email_triage"
TASKS = ["classify_email", "draft_response", "full_triage", "mood_based_triage"]
MAX_STEPS = 6  # 5 emails + 1 buffer
TEMPERATURE = 0.3
MAX_TOKENS = 400

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS PER TASK
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "classify_email": textwrap.dedent("""
        You are an expert email triage agent. Your job is to classify incoming emails.

        For each email, you must provide exactly TWO fields:
        1. priority: one of "low", "medium", "high", "urgent"
        2. category: one of "support", "sales", "billing", "technical", "spam"

        Classification guidelines:
        - urgent: Production outages, security incidents, system failures, data loss
        - high: Account access issues, billing errors, compliance deadlines
        - medium: Feature requests, plan changes, partnership inquiries, general questions
        - low: Positive feedback, informational notices, spam

        - support: Account help, how-to questions, feature requests, feedback, notifications
        - sales: Pricing inquiries, partnerships, enterprise deals, renewals
        - billing: Invoices, charges, refunds, plan changes, payment issues
        - technical: API errors, bugs, SSL/certificate issues, integration failures
        - spam: Lottery scams, phishing attempts, unsolicited suspicious emails

        Respond in this EXACT format (no other text):
        PRIORITY: <value>
        CATEGORY: <value>
    """).strip(),

    "draft_response": textwrap.dedent("""
        You are a professional customer service agent. Draft a helpful, professional
        response to the email you receive.

        Your response should:
        1. Address the sender by their name
        2. Acknowledge the specific issue or topic they mentioned
        3. Provide clear next steps or a helpful answer
        4. Maintain a professional and empathetic tone
        5. Be concise (50-150 words)

        Write ONLY the response text, as if you are replying to the email directly.
        Start with a greeting using the sender's name.
    """).strip(),

    "full_triage": textwrap.dedent("""
        You are an expert email triage agent performing full triage on incoming emails.

        For each email, provide ALL of the following:
        1. priority: one of "low", "medium", "high", "urgent"
        2. category: one of "support", "sales", "billing", "technical", "spam"
        3. routing_department: one of "customer_support", "sales", "billing", "engineering", "spam_filter"
        4. response: A professional draft reply (50-150 words)

        Routing guidelines:
        - customer_support: General support, how-to, feature requests, feedback
        - sales: Pricing, partnerships, enterprise deals, renewals
        - billing: Invoices, charges, refunds, plan changes
        - engineering: API issues, bugs, SSL, technical failures
        - spam_filter: Scam, phishing, suspicious emails

        Respond in this EXACT format:
        PRIORITY: <value>
        CATEGORY: <value>
        DEPARTMENT: <value>
        RESPONSE: <your draft response text>
    """).strip(),

    "mood_based_triage": textwrap.dedent("""
        You are an expert email triage agent equipped with a "Mood Box".
        You will receive a USER PROFILE (a resume or background summary) and a USER MOOD PROMPT (instructions on what to filter).
        Based on the user's mood and profile, decide whether to accept or reject the email.
        
        If the email strongly aligns with the user's specific goals and mood instructions, accept it.
        If the email is from a restricted source, purely promotional, or irrelevant to their mood, reject it.
        
        Respond in this EXACT format (no other text):
        ACTION: <accept or reject>
    """).strip(),
}


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Truncate action for readability
    action_short = action.replace("\n", " ")[:100]
    print(
        f"[STEP]  step={step} action={action_short} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END]   success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ACTION PARSING
# ─────────────────────────────────────────────────────────────────────────────

def parse_classify_response(text: str) -> Dict[str, str]:
    """Parse LLM output for classify_email task."""
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.upper().startswith("PRIORITY:"):
            result["priority"] = line.split(":", 1)[1].strip().lower().replace("*", "").replace('"', '')
        elif line.upper().startswith("CATEGORY:"):
            result["category"] = line.split(":", 1)[1].strip().lower().replace("*", "").replace('"', '')
    return result


def parse_mood_triage_response(text: str) -> Dict[str, str]:
    """Parse LLM output for mood_based_triage task."""
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.upper().startswith("ACTION:"):
            result["triage_action"] = line.split(":", 1)[1].strip().lower().replace("*", "").replace('"', '')
    return result


def parse_full_triage_response(text: str) -> Dict[str, str]:
    """Parse LLM output for full_triage task."""
    result = {}
    lines = text.strip().split("\n")
    response_lines = []
    in_response = False

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("PRIORITY:"):
            result["priority"] = stripped.split(":", 1)[1].strip().lower().replace("*", "").replace('"', '')
            in_response = False
        elif stripped.upper().startswith("CATEGORY:"):
            result["category"] = stripped.split(":", 1)[1].strip().lower().replace("*", "").replace('"', '')
            in_response = False
        elif stripped.upper().startswith("DEPARTMENT:"):
            result["routing_department"] = stripped.split(":", 1)[1].strip().lower().replace("*", "").replace('"', '')
            in_response = False
        elif stripped.upper().startswith("RESPONSE:"):
            response_text = stripped.split(":", 1)[1].strip()
            if response_text:
                response_lines.append(response_text)
            in_response = True
        elif in_response:
            response_lines.append(stripped)

    if response_lines:
        result["response"] = "\n".join(response_lines).strip()

    return result


# ─────────────────────────────────────────────────────────────────────────────
# LLM INTERACTION
# ─────────────────────────────────────────────────────────────────────────────

def get_model_response(
    client: OpenAI,
    task_type: str,
    email_subject: str,
    email_body: str,
    sender: str,
    sender_name: str,
    user_mood_prompt: str = "",
    user_profile: str = "",
) -> str:
    """Get LLM response for the given email and task."""
    system_prompt = SYSTEM_PROMPTS[task_type]

    user_prompt = textwrap.dedent(f"""
        USER PROFILE:
        {user_profile}
        
        USER MOOD PROMPT:
        {user_mood_prompt}
        
        FROM: {sender_name} <{sender}>
        SUBJECT: {email_subject}

        {email_body}
    """).strip()

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "No response generated."
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "Error: could not generate response."


def build_action(task_type: str, llm_output: str) -> EmailTriageAction:
    """Parse LLM output and build a typed action."""
    if task_type == "classify_email":
        parsed = parse_classify_response(llm_output)
        return EmailTriageAction(
            priority=parsed.get("priority"),
            category=parsed.get("category"),
        )
    elif task_type == "draft_response":
        return EmailTriageAction(response=llm_output)
    elif task_type == "full_triage":
        parsed = parse_full_triage_response(llm_output)
        return EmailTriageAction(
            priority=parsed.get("priority"),
            category=parsed.get("category"),
            response=parsed.get("response"),
            routing_department=parsed.get("routing_department"),
        )
    elif task_type == "mood_based_triage":
        parsed = parse_mood_triage_response(llm_output)
        return EmailTriageAction(
            triage_action=parsed.get("triage_action"),
        )
    else:
        return EmailTriageAction()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

async def run_task(client: OpenAI, env: EmailTriageEnv, task_type: str) -> float:
    """Run a single task and return the normalized score."""
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_type, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_type=task_type)
        obs = result.observation

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            # Get email from observation
            email_subject = obs.subject or ""
            email_body = obs.body or ""
            sender = obs.sender or ""
            sender_name = obs.sender_name or ""
            user_mood_prompt = getattr(obs, "user_mood_prompt", "") or ""
            user_profile = getattr(obs, "user_profile", "") or ""

            # Get LLM response
            llm_output = get_model_response(
                client, task_type, email_subject, email_body, sender, sender_name, user_mood_prompt, user_profile
            )

            # Build typed action
            action = build_action(task_type, llm_output)

            # Step the environment
            result = await env.step(action)
            obs = result.observation

            reward = result.reward or 0.0
            done = result.done
            error = obs.last_action_error if obs else None

            rewards.append(reward)
            steps_taken = step

            # Log with a summary of the action
            action_summary = f"priority={action.priority},category={action.category}"
            if task_type == "draft_response":
                action_summary = f"response='{(action.response or '')[:60]}...'"
            elif task_type == "full_triage":
                action_summary = (
                    f"priority={action.priority},category={action.category},"
                    f"dept={action.routing_department},response='{(action.response or '')[:40]}...'"
                )
            elif task_type == "mood_based_triage":
                action_summary = f"triage_action={action.triage_action}"

            log_step(
                step=step,
                action=action_summary,
                reward=reward,
                done=done,
                error=error,
            )

            if done:
                break

        # Compute normalized score (average reward per email)
        if rewards:
            score = sum(rewards) / len(rewards)
        # Ensure score is STRICTLY between 0 and 1
        score = min(max(score, 0.01), 0.99)
        success = score > 0.0

    except Exception as exc:
        print(f"[DEBUG] Task {task_type} failed: {exc}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


async def main() -> None:
    """Run all tasks sequentially."""
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    all_scores = {}

    for task_type in TASKS:
        # Create a fresh env connection for each task
        if LOCAL_IMAGE_NAME:
            env = await EmailTriageEnv.from_docker_image(LOCAL_IMAGE_NAME)
        else:
            # Connect to running HF Space or local server
            base_url = os.getenv("ENV_BASE_URL", "http://localhost:8000")
            env = EmailTriageEnv(base_url=base_url)
            await env.connect()

        try:
            score = await run_task(client, env, task_type)
            all_scores[task_type] = score
        finally:
            try:
                await env.close()
            except Exception as e:
                print(f"[DEBUG] env.close() error: {e}", flush=True)

    # Summary
    print("\n" + "=" * 60, flush=True)
    print("FINAL SCORES:", flush=True)
    for task, s in all_scores.items():
        print(f"  {task}: {s:.2f}", flush=True)
    avg = sum(all_scores.values()) / max(len(all_scores), 1)
    print(f"  AVERAGE: {avg:.2f}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
