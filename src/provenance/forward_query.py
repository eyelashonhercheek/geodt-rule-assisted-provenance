from __future__ import annotations

from typing import Dict, List

from src.uid.uid_generator import (
    generate_outcrop_uid,
    generate_record_uid,
    generate_sample_uid,
)
from src.utils.io_utils import group_by, index_by, load_csv


def forward_query(outcrop_id: str) -> Dict[str, object]:
    outcrops = index_by(load_csv("outcrops_demo.csv"), "outcrop_id")
    samples = load_csv("samples_demo.csv")
    records = load_csv("analytical_records_demo.csv")

    outcrop = outcrops.get(outcrop_id)
    if outcrop is None:
        raise ValueError(f"Unknown outcrop_id: {outcrop_id}")

    records_by_sample = group_by(records, "sample_id")
    linked_samples: List[Dict[str, object]] = []
    for sample in samples:
        if sample["outcrop_id"] != outcrop_id:
            continue
        sample_records = []
        for record in records_by_sample.get(sample["sample_id"], []):
            sample_records.append(
                {
                    **record,
                    "uid": generate_record_uid(record),
                }
            )

        linked_samples.append(
            {
                **sample,
                "uid": generate_sample_uid(sample),
                "analytical_records": sample_records,
            }
        )

    return {
        "outcrop": {
            **outcrop,
            "uid": generate_outcrop_uid(outcrop),
        },
        "samples": linked_samples,
    }
