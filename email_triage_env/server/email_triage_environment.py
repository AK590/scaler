"""
Email Triage Environment — Server-side implementation.

Implements the core environment logic: reset(), step(), state().
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
import random

from openenv.core.env_server.types import Action, Observation, State
from openenv.core.env_server.interfaces import Environment

from ..email_data import Email, get_task_emails, get_available_tasks
from ..graders import grade_classification, grade_response, grade_full_triage, grade_mood_triage
from ..models import EmailTriageAction, EmailTriageObservation, EmailTriageState


class EmailTriageEnvironment(Environment):
    """
    OpenEnv Environment for email triage tasks.

    The agent receives emails one at a time and must perform actions
    appropriate to the task type:

    - classify_email: classify priority and category
    - draft_response: write an appropriate reply
    - full_triage: classify, respond, and route the email

    Each episode consists of 5 emails. The reward for each step is
    in [0.0, 1.0] based on rubric-based grading.
    """

    def __init__(self):
        """Initialize the environment."""
        self._state = EmailTriageState(
            episode_id=str(uuid4()),
            step_count=0,
        )
        self._emails: List[Email] = []
        self._current_email: Optional[Email] = None
        self._is_reset = False

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs: Any,
    ) -> Observation:
        """
        Reset the environment for a new episode.

        Args:
            seed: Unused (deterministic dataset)
            episode_id: Optional custom episode ID
            task_type: One of 'classify_email', 'draft_response', 'full_triage'.
                       Defaults to 'classify_email'.

        Returns:
            Observation with the first email to process.
        """
        task_type = task_type or kwargs.get("task_type", "classify_email")
        available = get_available_tasks()
        if task_type not in available:
            task_type = "classify_email"

        self._emails = get_task_emails(task_type)
        if seed is not None:
            random.seed(seed)
        random.shuffle(self._emails)
        
        self._is_reset = True

        self._state = EmailTriageState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_type=task_type,
            current_email_index=0,
            total_emails=len(self._emails),
            cumulative_reward=0.0,
            rewards=[],
        )

        # Load first email
        self._current_email = self._emails[0] if self._emails else None

        obs = self._make_observation(
            reward=0.0,
            done=False,
            feedback="Episode started. Process the email below.",
        )

        return obs

    def step(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> Observation:
        """
        Process an agent action on the current email.

        Args:
            action: The Action from the agent. Expected to contain fields
                    matching EmailTriageAction.
            timeout_s: Unused.

        Returns:
            Observation with grading feedback and the next email (or done).
        """
        if not self._is_reset:
            return Observation(
                done=True,
                reward=0.0,
                metadata={
                    "last_action_error": "Environment not reset. Call reset() first.",
                },
            )

        self._state.step_count += 1

        # Parse action data — handle both EmailTriageAction (fields at top level)
        # and base Action (fields inside metadata dict)
        action_data = {}
        if hasattr(action, "model_dump"):
            dumped = action.model_dump()
            # If there's a 'metadata' key with action fields, merge it up
            if "metadata" in dumped and isinstance(dumped["metadata"], dict):
                action_data = {**dumped, **dumped["metadata"]}
            else:
                action_data = dumped
        elif hasattr(action, "metadata"):
            action_data = action.metadata
        elif isinstance(action, dict):
            action_data = action

        email = self._current_email
        if email is None:
            return Observation(
                done=True,
                reward=0.0,
                metadata={"last_action_error": "No email to process."},
            )

        # Grade based on task type
        task_type = self._state.task_type or "classify_email"
        reward, feedback = self._grade_action(action_data, email, task_type)

        # Record reward
        self._state.rewards.append(reward)
        self._state.cumulative_reward += reward

        # Advance to next email
        self._state.current_email_index += 1
        done = self._state.current_email_index >= self._state.total_emails

        if not done:
            self._current_email = self._emails[self._state.current_email_index]
        else:
            self._current_email = None

        obs = self._make_observation(
            reward=reward,
            done=done,
            feedback=feedback,
        )

        return obs

    def _grade_action(
        self, action_data: Dict[str, Any], email: Email, task_type: str
    ) -> tuple:
        """Grade an action using the appropriate grader."""
        priority = action_data.get("priority")
        category = action_data.get("category")
        response = action_data.get("response")
        department = action_data.get("routing_department")
        triage_action = action_data.get("triage_action")

        if task_type == "classify_email":
            return grade_classification(priority, category, email)
        elif task_type == "draft_response":
            return grade_response(response, email)
        elif task_type == "full_triage":
            return grade_full_triage(
                priority, category, response, department, email
            )
        elif task_type == "mood_based_triage":
            return grade_mood_triage(triage_action, email)
        else:
            return 0.0, f"Unknown task type: {task_type}"

    def _make_observation(
        self,
        reward: float,
        done: bool,
        feedback: str,
        error: Optional[str] = None,
    ) -> EmailTriageObservation:
        """Build an observation for the current state."""
        email = self._current_email
        
        user_mood_prompt = None
        user_profile = None
        if self._state.task_type == "mood_based_triage":
            user_mood_prompt = "I am a 3rd-year student looking for internships. Only send me solid internship opportunities. Block purely promotional Unstop challenges or Telegram groups."
            user_profile = "Resume: 3rd Year B.Tech CS. Skills: Python, React, APIs. Looking for Software Engineering Internships."

        return EmailTriageObservation(
            email_id=email.email_id if email else None,
            subject=email.subject if email else None,
            body=email.body if email else None,
            sender=email.sender if email else None,
            sender_name=email.sender_name if email else None,
            task_type=self._state.task_type,
            emails_remaining=max(
                0,
                self._state.total_emails - self._state.current_email_index
                - (0 if done else 0),
            ),
            feedback=feedback,
            last_action_error=error,
            done=done,
            reward=reward,
            user_mood_prompt=user_mood_prompt,
            user_profile=user_profile,
        )

    @property
    def state(self) -> State:
        """Return the current environment state."""
        return State(
            episode_id=self._state.episode_id,
            step_count=self._state.step_count,
            task_type=self._state.task_type,
            current_email_index=self._state.current_email_index,
            total_emails=self._state.total_emails,
            cumulative_reward=self._state.cumulative_reward,
        )

    def close(self) -> None:
        """Clean up resources (no-op for this environment)."""
        pass
