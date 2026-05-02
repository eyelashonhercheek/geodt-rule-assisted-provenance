from __future__ import annotations

from typing import Dict, List, Set

from src.association.evidence_operators import (
    candidates_by_id,
    candidates_by_source,
    candidates_by_stratigraphy,
    lithology_support,
)
from src.association.fallback import apply_constraint_with_fallback
from src.association.status import assign_status
from src.utils.io_utils import index_by, load_csv


Record = Dict[str, str]
Sample = Dict[str, str]


def infer_failure_reason(record: Record) -> str:
    """Map unresolved records to the paper's boundary-condition reasons."""
    has_source = bool((record.get("outcrop_norm") or "").strip() or (record.get("section_norm") or "").strip())
    has_strat = bool((record.get("strat_unit_norm") or "").strip())

    if not has_source and not has_strat:
        return "missing_source_and_stratigraphy"
    if not has_source:
        return "missing_source"
    return "outside_baseline"


def build_result(
    record: Record,
    final_candidates: Set[str],
    evidence_log: List[Dict[str, object]],
    status_info: Dict[str, str],
    entry_point: str,
    fallback_info: Dict[str, object],
) -> Dict[str, object]:
    """Create an association-layer recovery result for one analytical record."""
    return {
        "record_id": record["record_id"],
        "entry_point": entry_point,
        "final_candidates": sorted(final_candidates),
        "status": status_info["status"],
        "failure_reason": status_info.get("failure_reason", ""),
        "evidence_log": evidence_log,
        "fallback_info": fallback_info,
        "fallback_applied": bool(fallback_info.get("fallback_applied")),
    }


def _candidate_objects(candidate_ids: Set[str], baseline_samples: List[Sample]) -> List[Sample]:
    return [sample for sample in baseline_samples if sample["baseline_id"] in candidate_ids]


def recover_record_provenance(record: Record, baseline_samples: List[Sample]) -> Dict[str, object]:
    """Run evidence operators, fallback, and status assignment for one record."""
    evidence_log: List[Dict[str, object]] = []

    id_candidates, id_log = candidates_by_id(record, baseline_samples)
    evidence_log.append(id_log)

    if id_candidates:
        candidates = id_candidates
        entry_point = "identifier"
    else:
        source_candidates, source_log = candidates_by_source(record, baseline_samples)
        strat_candidates, strat_log = candidates_by_stratigraphy(record, baseline_samples)
        evidence_log.extend([source_log, strat_log])

        available_sets = [
            candidate_set
            for candidate_set, log in (
                (source_candidates, source_log),
                (strat_candidates, strat_log),
            )
            if log.get("available")
        ]

        if len(available_sets) == 2:
            candidates = source_candidates & strat_candidates
        elif len(available_sets) == 1:
            candidates = available_sets[0]
        else:
            candidates = set()
        entry_point = "context"

    if not candidates:
        status_info = assign_status(
            candidates,
            evidence_log,
            failure_reason=infer_failure_reason(record),
        )
        return build_result(
            record,
            candidates,
            evidence_log,
            status_info,
            entry_point,
            {
                "fallback_applied": False,
                "fallback_reason": "no_candidates_retained",
            },
        )

    lith_candidates, lith_log = lithology_support(
        record,
        _candidate_objects(candidates, baseline_samples),
    )
    evidence_log.append(lith_log)

    if lith_log.get("available"):
        constrained_candidates, fallback_log = apply_constraint_with_fallback(
            previous_candidates=candidates,
            filtered_candidates=lith_candidates,
            evidence_quality="weak",
            conflict=False,
        )
    else:
        constrained_candidates = candidates
        fallback_log = {
            "fallback_applied": False,
            "fallback_reason": "weak_evidence_unavailable",
        }
    evidence_log.append({"operator": "conservative_fallback", **fallback_log})

    status_info = assign_status(constrained_candidates, evidence_log)
    return build_result(
        record,
        constrained_candidates,
        evidence_log,
        status_info,
        entry_point,
        fallback_log,
    )


def recover_all_records() -> Dict[str, Dict[str, object]]:
    """Recover provenance for every demo analytical record."""
    baseline_samples = load_csv("baseline_samples_demo.csv")
    records = load_csv("analytical_records_demo.csv")
    return {
        result["record_id"]: result
        for result in (recover_record_provenance(record, baseline_samples) for record in records)
    }


def recover_record_by_id(record_id: str) -> Dict[str, object]:
    """Load one analytical record and recover its baseline-sample candidates."""
    records = index_by(load_csv("analytical_records_demo.csv"), "record_id")
    record = records.get(record_id)
    if record is None:
        raise ValueError(f"Unknown record_id: {record_id}")
    return recover_record_provenance(record, load_csv("baseline_samples_demo.csv"))
