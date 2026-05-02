from __future__ import annotations

from typing import Dict, List

from src.association.recovery import recover_all_records
from src.uid.uid_generator import (
    generate_outcrop_uid,
    generate_record_uid,
    generate_sample_uid,
)
from src.utils.io_utils import index_by, load_csv


def forward_query(outcrop_id: str) -> Dict[str, object]:
    """Trace from an outcrop through recovered association-layer results."""
    outcrops = index_by(load_csv("outcrops_demo.csv"), "outcrop_id")
    baseline_samples = load_csv("baseline_samples_demo.csv")
    records = index_by(load_csv("analytical_records_demo.csv"), "record_id")
    recovery_results = recover_all_records()

    outcrop = outcrops.get(outcrop_id)
    if outcrop is None:
        raise ValueError(f"Unknown outcrop_id: {outcrop_id}")

    linked_samples: List[Dict[str, object]] = []
    for sample in baseline_samples:
        if sample["outcrop_id"] != outcrop_id:
            continue

        linked_records = []
        for result in recovery_results.values():
            if sample["baseline_id"] not in result["final_candidates"]:
                continue
            record = records[result["record_id"]]
            linked_records.append(
                {
                    **record,
                    "uid": generate_record_uid(record),
                    "recovery_status": result["status"],
                    "candidate_count": len(result["final_candidates"]),
                }
            )

        linked_samples.append(
            {
                **sample,
                "uid": generate_sample_uid(sample),
                "analytical_records": linked_records,
            }
        )

    return {
        "outcrop": {
            **outcrop,
            "uid": generate_outcrop_uid(outcrop),
        },
        "baseline_samples": linked_samples,
    }
