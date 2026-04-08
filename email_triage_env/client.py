"""
Email Triage Environment Client.

Provides the EnvClient subclass for connecting to an Email Triage
Environment server via WebSocket.
"""

from typing import Any, Dict

from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult

from .models import EmailTriageAction, EmailTriageObservation, EmailTriageState


class EmailTriageEnv(EnvClient[EmailTriageAction, EmailTriageObservation, EmailTriageState]):
    """
    Client for the Email Triage Environment.

    Example (async):
        >>> async with EmailTriageEnv(base_url="http://localhost:8000") as env:
        ...     result = await env.reset(task_type="classify_email")
        ...     result = await env.step(EmailTriageAction(priority="high", category="support"))

    Example (sync):
        >>> with EmailTriageEnv(base_url="http://localhost:8000").sync() as env:
        ...     result = env.reset(task_type="classify_email")
        ...     result = env.step(EmailTriageAction(priority="high", category="support"))

    Example (Docker):
        >>> env = await EmailTriageEnv.from_docker_image("email-triage-env:latest")
        >>> result = await env.reset(task_type="classify_email")
    """

    def _step_payload(self, action: EmailTriageAction) -> Dict[str, Any]:
        """Convert EmailTriageAction to JSON payload for the server."""
        return action.model_dump(exclude_none=True)

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[EmailTriageObservation]:
        """Parse server response into StepResult[EmailTriageObservation]."""
        obs_data = payload.get("observation", payload)
        reward = payload.get("reward", obs_data.get("reward"))
        done = payload.get("done", obs_data.get("done", False))

        observation = EmailTriageObservation(
            email_id=obs_data.get("email_id"),
            subject=obs_data.get("subject"),
            body=obs_data.get("body"),
            sender=obs_data.get("sender"),
            sender_name=obs_data.get("sender_name"),
            task_type=obs_data.get("task_type"),
            emails_remaining=obs_data.get("emails_remaining", 0),
            feedback=obs_data.get("feedback"),
            last_action_error=obs_data.get("last_action_error"),
            done=done,
            reward=reward,
            user_mood_prompt=obs_data.get("user_mood_prompt"),
            user_profile=obs_data.get("user_profile"),
        )

        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
        )

    def _parse_state(self, payload: Dict[str, Any]) -> EmailTriageState:
        """Parse server state response into EmailTriageState."""
        return EmailTriageState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_type=payload.get("task_type"),
            current_email_index=payload.get("current_email_index", 0),
            total_emails=payload.get("total_emails", 0),
            cumulative_reward=payload.get("cumulative_reward", 0.0),
        )
