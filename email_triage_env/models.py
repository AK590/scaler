"""
Typed models for the Email Triage Environment.

Defines Pydantic-based Action, Observation, and State models
for the OpenEnv Email Triage environment.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

try:
    from openenv.core.env_server.types import Observation as _BaseObservation
except ImportError:
    _BaseObservation = None  # type: ignore



# ─────────────────────────────────────────────────────────────────────────────
# ACTION
# ─────────────────────────────────────────────────────────────────────────────

class EmailTriageAction(BaseModel):
    """Action the agent submits each step.

    Depending on the task, different fields are relevant:
    - classify_email: priority, category
    - draft_response: response
    - full_triage: all fields
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    priority: Optional[str] = Field(
        default=None,
        description="Email priority: low, medium, high, or urgent",
    )
    category: Optional[str] = Field(
        default=None,
        description="Email category: support, sales, billing, technical, or spam",
    )
    response: Optional[str] = Field(
        default=None,
        description="Draft response text to the email",
    )
    routing_department: Optional[str] = Field(
        default=None,
        description="Department to route to: customer_support, sales, billing, engineering, or spam_filter",
    )
    triage_action: Optional[str] = Field(
        default=None,
        description="Decision for mood-based triage: 'accept' or 'reject'",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the action",
    )


# ─────────────────────────────────────────────────────────────────────────────
# OBSERVATION
# ─────────────────────────────────────────────────────────────────────────────

# Choose base class: use OpenEnv Observation if available
_ObsBase = _BaseObservation if _BaseObservation is not None else BaseModel


class EmailTriageObservation(_ObsBase):
    """Observation returned to the agent after reset/step.

    Contains the current email to process plus feedback from the
    previous action. Inherits done, reward, and metadata from the
    OpenEnv Observation base class.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    email_id: Optional[str] = Field(
        default=None,
        description="Unique ID of the current email",
    )
    subject: Optional[str] = Field(
        default=None,
        description="Subject line of the current email",
    )
    body: Optional[str] = Field(
        default=None,
        description="Body text of the current email",
    )
    sender: Optional[str] = Field(
        default=None,
        description="Sender email address",
    )
    sender_name: Optional[str] = Field(
        default=None,
        description="Sender's display name",
    )
    task_type: Optional[str] = Field(
        default=None,
        description="Current task type: classify_email, draft_response, or full_triage",
    )
    emails_remaining: int = Field(
        default=0,
        description="Number of emails remaining in the episode",
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Feedback from the grader on the last action",
    )
    last_action_error: Optional[str] = Field(
        default=None,
        description="Error message if the last action was invalid",
    )
    user_mood_prompt: Optional[str] = Field(
        default=None,
        description="Contextual mood or instructions set by the user",
    )
    user_profile: Optional[str] = Field(
        default=None,
        description="Brief resume, background, or user profile string",
    )



# ─────────────────────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────────────────────

class EmailTriageState(BaseModel):
    """Internal environment state for tracking the episode."""

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
    )

    episode_id: Optional[str] = Field(
        default=None,
        description="Unique episode identifier",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Steps taken in current episode",
    )
    task_type: Optional[str] = Field(
        default=None,
        description="Current task type",
    )
    current_email_index: int = Field(
        default=0,
        description="Index of current email in the episode queue",
    )
    total_emails: int = Field(
        default=0,
        description="Total emails in the episode",
    )
    cumulative_reward: float = Field(
        default=0.0,
        description="Sum of rewards across all steps",
    )
    rewards: List[float] = Field(
        default_factory=list,
        description="Per-step rewards",
    )
