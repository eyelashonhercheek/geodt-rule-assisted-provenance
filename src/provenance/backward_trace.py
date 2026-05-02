from __future__ import annotations

from typing import Dict, List

from src.association.recovery import recover_record_by_id
from src.uid.uid_generator import (
    generate_outcrop_uid,
    generate_record_uid,
    generate_sample_uid,
)
from src.utils.io_utils import index_by, load_csv


def backward_trace(record_id: str) -> Dict[str, object]:
    """Trace one analytical record to recovered candidate samples and outcrops."""
    outcrops = index_by(load_csv("outcrops_demo.csv"), "outcrop_id")
    baseline_samples = index_by(load_csv("baseline_samples_demo.csv"), "baseline_id")
    records = index_by(load_csv("analytical_records_demo.csv"), "record_id")

    record = records.get(record_id)
    if record is None:
        raise ValueError(f"Unknown record_id: {record_id}")

    recovery_result = recover_record_by_id(record_id)
    if recovery_result["status"] == "unresolved":
        return {
            "record": {
                **record,
                "uid": generate_record_uid(record),
            },
            "status": recovery_result["status"],
            "failure_reason": recovery_result["failure_reason"],
            "trace": [],
        }

    traces: List[Dict[str, object]] = []
    for baseline_id in recovery_result["final_candidates"]:
        sample = baseline_samples[baseline_id]
        outcrop = outcrops.get(sample["outcrop_id"])
        traces.append(
            {
                "baseline_sample": {
                    **sample,
                    "uid": generate_sample_uid(sample),
                },
                "outcrop": {
                    **outcrop,
                    "uid": generate_outcrop_uid(outcrop),
                }
                if outcrop
                else None,
            }
        )

    return {
        "record": {
            **record,
            "uid": generate_record_uid(record),
        },
        "status": recovery_result["status"],
        "failure_reason": recovery_result["failure_reason"],
        "trace": traces,
    }
