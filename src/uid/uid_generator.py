from __future__ import annotations

from typing import Dict


LEVEL_CODES = {
    "outcrop": "OUTCROP",
    "sample": "SAMPLE",
    "record": "RECORD",
}


def _slug(value: str) -> str:
    cleaned = (value or "").strip().upper().replace(" ", "_")
    return cleaned.replace("/", "_").replace("-", "_")


def generate_uid(
    *,
    level: str,
    reg: str,
    age: str,
    seq: str,
    sub: str | None = None,
) -> str:
    if level not in LEVEL_CODES:
        raise ValueError(f"Unsupported level: {level}")

    parts = [
        LEVEL_CODES[level],
        _slug(reg),
        _slug(age),
        _slug(seq),
    ]
    if sub:
        parts.append(_slug(sub))
    return "-".join(parts)


def generate_outcrop_uid(outcrop: Dict[str, str]) -> str:
    return generate_uid(
        level="outcrop",
        reg=outcrop["region_tag"],
        age=outcrop["stratigraphy"],
        seq=outcrop["outcrop_id"],
        sub=outcrop["lithology"].split()[-1],
    )


def generate_sample_uid(sample: Dict[str, str]) -> str:
    return generate_uid(
        level="sample",
        reg=sample["source_info"],
        age=sample["stratigraphy"],
        seq=sample["sample_id"],
        sub="handspecimen",
    )


def generate_record_uid(record: Dict[str, str]) -> str:
    return generate_uid(
        level="record",
        reg=record["source_info"],
        age=record["stratigraphy"],
        seq=record["record_id"],
        sub=record["analysis_type"],
    )
