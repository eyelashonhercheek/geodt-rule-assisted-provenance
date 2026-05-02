from __future__ import annotations

from typing import Dict, Set, Tuple


def apply_constraint_with_fallback(
    previous_candidates: Set[str],
    filtered_candidates: Set[str],
    evidence_quality: str,
    conflict: bool = False,
) -> Tuple[Set[str], Dict[str, object]]:
    """Preserve auditability when weak evidence would erase retained candidates."""
    if filtered_candidates:
        return filtered_candidates, {
            "fallback_applied": False,
            "fallback_reason": "constraint_retained_candidates",
        }

    if evidence_quality == "weak" and previous_candidates:
        return previous_candidates, {
            "fallback_applied": True,
            "fallback_reason": "weak_evidence_should_not_clear_candidates",
        }

    if conflict:
        return set(), {
            "fallback_applied": False,
            "fallback_reason": "high_confidence_conflict",
        }

    return filtered_candidates, {
        "fallback_applied": False,
        "fallback_reason": "no_candidates_retained",
    }
