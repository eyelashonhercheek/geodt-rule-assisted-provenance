from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.association.recovery import recover_all_records
from src.utils.io_utils import load_csv


def main() -> None:
    """Validate demo recovery outputs against the paper-oriented expected cases."""
    results = recover_all_records()
    expected_rows = load_csv("expected_linkage_results_demo.csv")
    failures = []

    for expected in expected_rows:
        record_id = expected["record_id"]
        actual = results[record_id]
        expected_candidates = [
            item for item in expected["expected_candidates"].split("|") if item
        ]

        if actual["status"] != expected["expected_status"]:
            failures.append(
                f"{record_id}: status {actual['status']!r} != {expected['expected_status']!r}"
            )
        if actual["final_candidates"] != expected_candidates:
            failures.append(
                f"{record_id}: candidates {actual['final_candidates']!r} != {expected_candidates!r}"
            )
        if actual["failure_reason"] != expected["expected_failure_reason"]:
            failures.append(
                f"{record_id}: failure_reason {actual['failure_reason']!r} "
                f"!= {expected['expected_failure_reason']!r}"
            )

    if failures:
        print("Expected-result validation failed")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(f"Expected-result validation passed for {len(expected_rows)} records.")


if __name__ == "__main__":
    main()
