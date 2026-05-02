from __future__ import annotations

from typing import Dict, List

from src.association.recovery import recover_record_by_id


def _format_evidence(entry: Dict[str, object]) -> str:
    operator = entry.get("operator")
    if operator == "conservative_fallback":
        applied = "applied" if entry.get("fallback_applied") else "not applied"
        return f"{operator}: {applied}; reason={entry.get('fallback_reason')}"

    availability = "available" if entry.get("available") else "not available"
    matched = "matched" if entry.get("matched") else "not matched"
    count = entry.get("candidate_count", 0)
    strength = entry.get("strength", "")
    message = entry.get("message", "")
    return (
        f"{operator}: {availability}, {matched}, strength={strength}, "
        f"candidates={count}; {message}"
    )


def recovery_example_lines(record_id: str) -> List[str]:
    """Format one recovery result for the runnable paper demo."""
    result = recover_record_by_id(record_id)
    candidates = result["final_candidates"] or ["none"]

    lines = [
        f"Record: {record_id}",
        f"Entry point: {result['entry_point']}",
        "",
        "Final candidates:",
    ]
    lines.extend(f"  {candidate}" for candidate in candidates)
    lines.extend(
        [
            "",
            "Status:",
            f"  {result['status']}",
        ]
    )
    if result["failure_reason"]:
        lines.extend(["", "Failure reason:", f"  {result['failure_reason']}"])

    fallback_info = result["fallback_info"]
    lines.extend(
        [
            "",
            "Fallback information:",
            f"  applied={fallback_info['fallback_applied']}",
            f"  reason={fallback_info['fallback_reason']}",
        ]
    )

    lines.extend(["", "Evidence log:"])
    lines.extend(f"  - {_format_evidence(entry)}" for entry in result["evidence_log"])
    return lines
