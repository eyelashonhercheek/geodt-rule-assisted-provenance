from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple


EvidenceLog = Dict[str, object]
Record = Dict[str, str]
Sample = Dict[str, str]


def _value(row: Dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def _candidate_ids(rows: Iterable[Sample]) -> Set[str]:
    return {row["baseline_id"] for row in rows}


def candidates_by_id(record: Record, baseline_samples: List[Sample]) -> Tuple[Set[str], EvidenceLog]:
    """Generate candidates from high-confidence normalized identifier evidence."""
    sample_id = _value(record, "sample_id_norm")
    if not sample_id:
        return set(), {
            "operator": "F_id",
            "available": False,
            "matched": False,
            "strength": "high",
            "evidence": "sample_id_norm",
            "candidate_count": 0,
            "message": "sample_id_norm is not available",
        }

    candidates = _candidate_ids(
        sample for sample in baseline_samples if _value(sample, "sample_id_norm") == sample_id
    )
    return candidates, {
        "operator": "F_id",
        "available": True,
        "matched": bool(candidates),
        "strength": "high",
        "evidence": "sample_id_norm",
        "candidate_count": len(candidates),
        "message": "sample_id_norm matched baseline sample"
        if candidates
        else "sample_id_norm did not match the baseline sample space",
    }


def candidates_by_source(record: Record, baseline_samples: List[Sample]) -> Tuple[Set[str], EvidenceLog]:
    """Generate contextual candidates from normalized outcrop or section fields."""
    outcrop_norm = _value(record, "outcrop_norm")
    section_norm = _value(record, "section_norm")
    if not outcrop_norm and not section_norm:
        return set(), {
            "operator": "F_src",
            "available": False,
            "matched": False,
            "strength": "contextual",
            "evidence": "outcrop_norm/section_norm",
            "candidate_count": 0,
            "message": "source and section evidence are not available",
        }

    candidates = set()
    for sample in baseline_samples:
        outcrop_match = bool(outcrop_norm and outcrop_norm == _value(sample, "outcrop_norm"))
        section_match = bool(section_norm and section_norm == _value(sample, "section_norm"))
        if outcrop_match or section_match:
            candidates.add(sample["baseline_id"])

    return candidates, {
        "operator": "F_src",
        "available": True,
        "matched": bool(candidates),
        "strength": "contextual",
        "evidence": "outcrop_norm/section_norm",
        "candidate_count": len(candidates),
        "message": "source or section evidence retained baseline candidates"
        if candidates
        else "source or section evidence retained no baseline candidates",
    }


def candidates_by_stratigraphy(record: Record, baseline_samples: List[Sample]) -> Tuple[Set[str], EvidenceLog]:
    """Generate or constrain candidates from normalized stratigraphic evidence."""
    strat_unit = _value(record, "strat_unit_norm")
    if not strat_unit:
        return set(), {
            "operator": "F_strat",
            "available": False,
            "matched": False,
            "strength": "contextual",
            "evidence": "strat_unit_norm",
            "candidate_count": 0,
            "message": "stratigraphic evidence is not available",
        }

    candidates = _candidate_ids(
        sample for sample in baseline_samples if _value(sample, "strat_unit_norm") == strat_unit
    )
    return candidates, {
        "operator": "F_strat",
        "available": True,
        "matched": bool(candidates),
        "strength": "contextual",
        "evidence": "strat_unit_norm",
        "candidate_count": len(candidates),
        "message": "stratigraphic evidence retained baseline candidates"
        if candidates
        else "stratigraphic evidence retained no baseline candidates",
    }


def lithology_support(record: Record, candidate_samples: List[Sample]) -> Tuple[Set[str], EvidenceLog]:
    """Apply lithology as weak support over an existing candidate set."""
    lithology = _value(record, "lithology_norm")
    if not lithology:
        return set(), {
            "operator": "F_lith",
            "available": False,
            "matched": False,
            "evidence": "lithology_norm",
            "strength": "weak",
            "candidate_count": 0,
            "message": "lithology evidence is not available",
        }

    supported = _candidate_ids(
        sample for sample in candidate_samples if _value(sample, "lithology_norm") == lithology
    )
    return supported, {
        "operator": "F_lith",
        "available": True,
        "matched": bool(supported),
        "evidence": "lithology_norm",
        "strength": "weak",
        "candidate_count": len(supported),
        "message": "lithology weakly supported retained candidates"
        if supported
        else "lithology did not support the retained candidates",
    }
