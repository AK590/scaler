"""
Graders for the Email Triage Environment.

Deterministic, rubric-based grading functions that produce scores in [0.0, 1.0]
with partial progress signals. No LLM-as-judge — fully reproducible.
"""

import re
from typing import Dict, Optional, Tuple

from .email_data import Email, VALID_CATEGORIES, VALID_DEPARTMENTS, VALID_PRIORITIES


def _normalize(text: str) -> str:
    """Lowercase and strip whitespace."""
    return text.strip().lower()


def _clamp_score(score: float) -> float:
    """Clamp score strictly within (0, 1) to satisfy validation constraints."""
    return max(0.01, min(float(score), 0.99))


# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION GRADER (Easy Task)
# ─────────────────────────────────────────────────────────────────────────────

def grade_classification(
    priority: Optional[str],
    category: Optional[str],
    email: Email,
) -> Tuple[float, str]:
    """
    Grade classification accuracy.

    Returns:
        (score, feedback) where score is in [0.0, 1.0]
        - 0.5 for correct priority
        - 0.5 for correct category
    """
    score = 0.0
    feedback_parts = []

    # Grade priority (0.5 points)
    if priority is not None:
        norm_priority = _normalize(priority)
        if norm_priority == email.ground_truth_priority:
            score += 0.5
            feedback_parts.append(f"Priority correct ({norm_priority})")
        elif norm_priority in VALID_PRIORITIES:
            # Partial credit for close misses on the priority scale
            priority_scale = ["low", "medium", "high", "urgent"]
            try:
                pred_idx = priority_scale.index(norm_priority)
                true_idx = priority_scale.index(email.ground_truth_priority)
                distance = abs(pred_idx - true_idx)
                if distance == 1:
                    score += 0.2  # one level off
                    feedback_parts.append(
                        f"Priority close (predicted {norm_priority}, "
                        f"expected {email.ground_truth_priority})"
                    )
                else:
                    feedback_parts.append(
                        f"Priority wrong (predicted {norm_priority}, "
                        f"expected {email.ground_truth_priority})"
                    )
            except ValueError:
                feedback_parts.append(f"Invalid priority: {norm_priority}")
        else:
            feedback_parts.append(
                f"Invalid priority '{priority}'. "
                f"Valid: {', '.join(sorted(VALID_PRIORITIES))}"
            )
    else:
        feedback_parts.append("Priority not provided")

    # Grade category (0.5 points)
    if category is not None:
        norm_category = _normalize(category)
        if norm_category == email.ground_truth_category:
            score += 0.5
            feedback_parts.append(f"Category correct ({norm_category})")
        elif norm_category in VALID_CATEGORIES:
            feedback_parts.append(
                f"Category wrong (predicted {norm_category}, "
                f"expected {email.ground_truth_category})"
            )
        else:
            feedback_parts.append(
                f"Invalid category '{category}'. "
                f"Valid: {', '.join(sorted(VALID_CATEGORIES))}"
            )
    else:
        feedback_parts.append("Category not provided")

    return _clamp_score(score), "; ".join(feedback_parts)


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE GRADER (Medium Task)
# ─────────────────────────────────────────────────────────────────────────────

def grade_response(
    response: Optional[str],
    email: Email,
) -> Tuple[float, str]:
    """
    Grade draft response quality using a 4-dimension rubric.

    Each dimension is worth 0.25:
    1. Addresses sender by name
    2. Acknowledges the topic/issue
    3. Provides a relevant next step or solution
    4. Professional tone (appropriate length, no obvious issues)

    Returns:
        (score, feedback) where score is in [0.0, 1.0]
    """
    if response is None or len(response.strip()) == 0:
        return _clamp_score(0.0), "No response provided"

    response_lower = response.lower()
    score = 0.0
    feedback_parts = []

    # 1. Addresses sender by name (0.25)
    sender_name_parts = email.sender_name.lower().split()
    if any(part in response_lower for part in sender_name_parts if len(part) > 2):
        score += 0.25
        feedback_parts.append("Addressed sender by name")
    else:
        feedback_parts.append(
            f"Did not address sender by name (expected: {email.sender_name})"
        )

    # 2. Acknowledges the topic/issue (0.25)
    # Check if response mentions key topic words from the email
    topic_keywords = email.expected_response_keywords[:5]  # first 5 are topic-related
    topic_matches = sum(
        1 for kw in topic_keywords
        if kw.lower() in response_lower
    )
    topic_ratio = topic_matches / max(len(topic_keywords), 1)
    if topic_ratio >= 0.4:  # at least 2 out of 5 keywords
        score += 0.25
        feedback_parts.append(
            f"Acknowledged topic ({topic_matches}/{len(topic_keywords)} keywords)"
        )
    elif topic_ratio > 0:
        partial = 0.25 * topic_ratio
        score += partial
        feedback_parts.append(
            f"Partially acknowledged topic ({topic_matches}/{len(topic_keywords)} keywords)"
        )
    else:
        feedback_parts.append("Did not acknowledge the email's topic")

    # 3. Provides next step or solution (0.25)
    action_phrases = [
        "will", "we'll", "i'll", "let me", "please", "next step",
        "follow up", "investigate", "look into", "assist", "help",
        "get back", "reach out", "resolve", "fix", "update",
        "contact", "schedule", "review", "ensure", "working on",
    ]
    action_matches = sum(
        1 for phrase in action_phrases
        if phrase in response_lower
    )
    if action_matches >= 2:
        score += 0.25
        feedback_parts.append("Provided actionable next steps")
    elif action_matches == 1:
        score += 0.15
        feedback_parts.append("Partially provided next steps")
    else:
        feedback_parts.append("No clear next steps or resolution offered")

    # 4. Professional tone (0.25)
    tone_score = 0.25
    tone_issues = []

    # Check length
    word_count = len(response.split())
    if word_count < 15:
        tone_score -= 0.10
        tone_issues.append("too short")
    elif word_count > 500:
        tone_score -= 0.05
        tone_issues.append("overly verbose")

    # Check for all caps (shouting)
    caps_ratio = sum(1 for c in response if c.isupper()) / max(len(response), 1)
    if caps_ratio > 0.5 and word_count > 5:
        tone_score -= 0.10
        tone_issues.append("too many caps")

    # Check for basic professionalism indicators
    professional_phrases = [
        "thank", "regards", "best", "sincerely", "please",
        "appreciate", "sorry", "apologize", "happy to"
    ]
    has_professional = any(p in response_lower for p in professional_phrases)
    if not has_professional:
        tone_score -= 0.05
        tone_issues.append("lacks professional courtesy phrases")

    tone_score = max(tone_score, 0.0)
    score += tone_score

    if tone_issues:
        feedback_parts.append(f"Tone issues: {', '.join(tone_issues)}")
    else:
        feedback_parts.append("Professional tone")

    return _clamp_score(round(score, 4)), "; ".join(feedback_parts)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTING GRADER (used in Full Triage)
# ─────────────────────────────────────────────────────────────────────────────

def grade_routing(
    department: Optional[str],
    email: Email,
) -> Tuple[float, str]:
    """
    Grade routing department accuracy.

    Returns:
        (score, feedback) where score is in [0.0, 1.0]
    """
    if department is None:
        return _clamp_score(0.0), "No routing department provided"

    norm_dept = _normalize(department)

    if norm_dept == email.ground_truth_department:
        return _clamp_score(1.0), f"Correct routing ({norm_dept})"
    elif norm_dept in VALID_DEPARTMENTS:
        return _clamp_score(0.0), (
            f"Wrong routing (predicted {norm_dept}, "
            f"expected {email.ground_truth_department})"
        )
    else:
        return _clamp_score(0.0), (
            f"Invalid department '{department}'. "
            f"Valid: {', '.join(sorted(VALID_DEPARTMENTS))}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FULL TRIAGE GRADER (Hard Task)
# ─────────────────────────────────────────────────────────────────────────────

def grade_full_triage(
    priority: Optional[str],
    category: Optional[str],
    response: Optional[str],
    department: Optional[str],
    email: Email,
) -> Tuple[float, str]:
    """
    Grade full triage as a composite of sub-tasks.

    Weights:
    - 0.25: Priority classification
    - 0.25: Category classification
    - 0.25: Response quality
    - 0.25: Routing department

    Returns:
        (score, feedback) where score is in [0.0, 1.0]
    """
    feedback_parts = []

    # Priority (0.25 weight → classification gives 0-1.0, multiply by 0.5 then take priority portion)
    classification_score, classification_feedback = grade_classification(
        priority, category, email
    )
    # classification_score is already out of 1.0 (0.5 for priority, 0.5 for category)
    priority_portion = classification_score  # already 0-1.0
    feedback_parts.append(f"Classification: {classification_feedback}")

    # Response quality (0.25 weight)
    response_score, response_feedback = grade_response(response, email)
    feedback_parts.append(f"Response: {response_feedback}")

    # Routing (0.25 weight)
    routing_score, routing_feedback = grade_routing(department, email)
    feedback_parts.append(f"Routing: {routing_feedback}")

    # Composite: classification gets 0.5 (split between priority and category already),
    # response gets 0.25, routing gets 0.25
    total_score = (
        classification_score * 0.50  # priority + category already weighted equally
        + response_score * 0.25
        + routing_score * 0.25
    )

    total_score = round(min(max(total_score, 0.0), 1.0), 4)

    return _clamp_score(total_score), "; ".join(feedback_parts)


# ─────────────────────────────────────────────────────────────────────────────
# MOOD-BASED TRIAGE GRADER
# ─────────────────────────────────────────────────────────────────────────────

def grade_mood_triage(
    triage_action: Optional[str],
    email: Email,
) -> Tuple[float, str]:
    """
    Grade mood based triage logic.

    Returns:
        (score, feedback) where score is in [0.0, 1.0]
    """
    if triage_action is None:
        return _clamp_score(0.0), "No triage action provided"

    norm_action = _normalize(triage_action)

    if norm_action == email.ground_truth_triage_action:
        return _clamp_score(1.0), f"Correct action ({norm_action})"
    elif norm_action in ["accept", "reject"]:
        return _clamp_score(0.0), (
            f"Wrong action (predicted {norm_action}, "
            f"expected {email.ground_truth_triage_action})"
        )
    else:
        return _clamp_score(0.0), (
            f"Invalid action '{triage_action}'. "
            f"Valid: accept, reject"
        )
