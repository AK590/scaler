"""
Email Triage Environment — OpenEnv Environment for email classification,
response drafting, and routing.

An AI agent receives emails and must classify, respond to, and route them
correctly based on the task type.

Tasks:
    - classify_email (easy): Classify priority and category
    - draft_response (medium): Draft an appropriate reply
    - full_triage (hard): Classify, respond, and route
"""

from .models import EmailTriageAction, EmailTriageObservation, EmailTriageState
from .client import EmailTriageEnv

__all__ = [
    "EmailTriageAction",
    "EmailTriageObservation",
    "EmailTriageState",
    "EmailTriageEnv",
]
