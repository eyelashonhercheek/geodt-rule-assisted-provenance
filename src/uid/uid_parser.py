from __future__ import annotations

from typing import Dict


UID_FIELDS = [
    "level",
    "reg",
    "age",
    "seq",
    "sub",
]


def parse_uid(uid: str) -> Dict[str, str]:
    parts = uid.split("-")
    if len(parts) not in (4, 5):
        raise ValueError(f"Invalid UID: {uid}")
    if len(parts) == 4:
        parts.append("")
    return dict(zip(UID_FIELDS, parts))
