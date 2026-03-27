from __future__ import annotations

from typing import Dict

from src.uid.uid_generator import (
    generate_outcrop_uid,
    generate_record_uid,
    generate_sample_uid,
)
from src.utils.io_utils import index_by, load_csv


def backward_trace(record_id: str) -> Dict[str, object]:
    outcrops = index_by(load_csv("outcrops_demo.csv"), "outcrop_id")
    samples = index_by(load_csv("samples_demo.csv"), "sample_id")
    records = index_by(load_csv("analytical_records_demo.csv"), "record_id")

    record = records.get(record_id)
    if record is None:
        raise ValueError(f"Unknown record_id: {record_id}")

    sample = samples.get(record["sample_id"])
    if sample is None:
        raise ValueError(f"Broken provenance chain, sample not found: {record['sample_id']}")

    outcrop = outcrops.get(sample["outcrop_id"])
    if outcrop is None:
        raise ValueError(f"Broken provenance chain, outcrop not found: {sample['outcrop_id']}")

    return {
        "record": {
            **record,
            "uid": generate_record_uid(record),
        },
        "sample": {
            **sample,
            "uid": generate_sample_uid(sample),
        },
        "outcrop": {
            **outcrop,
            "uid": generate_outcrop_uid(outcrop),
        },
    }
