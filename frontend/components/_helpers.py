from typing import Tuple


def get_score_color(score: float) -> Tuple[str, str]:
    """
    Return (text_color, background_color) for a 0-100 score.
    Matches the .alert-success / .alert-warning / .alert-danger palette
    in assets/style.css, so score cards look consistent with the rest
    of the theme instead of using light-mode pastels.
    """
    if score >= 80:
        return "#9FD48C", "rgba(107, 159, 94, 0.16)"   # success
    if score >= 60:
        return "#E3C48A", "rgba(201, 161, 94, 0.16)"   # warning
    return "#E39990", "rgba(193, 102, 92, 0.16)"        # danger


def get_score_emoji(score: float) -> str:
    """Emoji that matches the score band — used in headlines."""
    if score >= 90:
        return "🌟"
    if score >= 80:
        return "✅"
    if score >= 70:
        return "👍"
    if score >= 60:
        return "⚠️"
    return "🔴"


def get_severity_style(severity: str) -> Tuple[str, str, str]:
    """
    Return (icon, text_color, background_color) for an IssueDetail severity.
    Matches the values the backend emits in `detailed_feedback[].severity_level`.
    Colors match the .alert-* palette in assets/style.css.
    """
    level = (severity or "").lower()
    if level in ("critical", "high"):
        return "🔴", "#E39990", "rgba(193, 102, 92, 0.16)"   # danger
    if level == "medium":
        return "🟡", "#E3C48A", "rgba(201, 161, 94, 0.16)"   # warning
    return "🟢", "#9FD48C", "rgba(107, 159, 94, 0.16)"        # success