from __future__ import annotations

from typing import Dict, List, Set


def assign_status(
    final_candidates: Set[str],
    evidence_log: List[Dict[str, object]],
    failure_reason: str = "",
) -> Dict[str, str]:
    """Assign the paper's hierarchical recovery status from retained candidates."""
    if not final_candidates:
        return {
            "status": "unresolved",
            "failure_reason": failure_reason or "no_reliable_candidate",
        }

    has_high_confidence_id = any(
        entry.get("operator") == "F_id" and entry.get("matched") for entry in evidence_log
    )
    has_conflict = any(entry.get("conflict") is True for entry in evidence_log)
    used_weak_evidence = any(
        entry.get("strength") == "weak" and entry.get("matched") for entry in evidence_log
    )

    if len(final_candidates) == 1 and has_high_confidence_id and not has_conflict:
        return {"status": "rule-supported link", "failure_reason": ""}

    if len(final_candidates) == 1 and (used_weak_evidence or not has_high_confidence_id):
        return {"status": "strong candidate", "failure_reason": ""}

    if len(final_candidates) > 1:
        return {"status": "candidate set", "failure_reason": ""}

    return {
        "status": "unresolved",
        "failure_reason": failure_reason or "no_reliable_candidate",
    }
