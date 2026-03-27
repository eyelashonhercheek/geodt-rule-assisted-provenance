from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.uid.uid_generator import (
    generate_outcrop_uid,
    generate_record_uid,
    generate_sample_uid,
)
from src.uid.uid_parser import parse_uid
from src.utils.io_utils import load_csv


def main() -> None:
    outcrop = load_csv("outcrops_demo.csv")[0]
    sample = load_csv("samples_demo.csv")[0]
    record = load_csv("analytical_records_demo.csv")[0]

    items = [
        ("outcrop", generate_outcrop_uid(outcrop)),
        ("sample", generate_sample_uid(sample)),
        ("record", generate_record_uid(record)),
    ]

    print("UID demo")
    print("=" * 60)
    for label, uid in items:
        print(f"{label}: {uid}")
        print(f"parsed: {parse_uid(uid)}")
        print("-" * 60)


if __name__ == "__main__":
    main()
