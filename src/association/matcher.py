from __future__ import annotations

from typing import Dict

from src.association.recovery import recover_record_by_id


def match_record_to_baseline_samples(record_id: str) -> Dict[str, object]:
    """Compatibility wrapper around the recovery workflow."""
    return recover_record_by_id(record_id)


def match_candidates(record_id: str) -> Dict[str, object]:
    """Backward-compatible name for candidate recovery."""
    return match_record_to_baseline_samples(record_id)
