from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.provenance.backward_trace import backward_trace
from src.provenance.forward_query import forward_query


def print_forward() -> None:
    """Show outcrop-to-record tracing through recovered links."""
    result = forward_query("OC002")
    print("Forward query over recovered association-layer outputs")
    print("=" * 60)
    print(f"Outcrop: {result['outcrop']['outcrop_id']} | uid={result['outcrop']['uid']}")
    for sample in result["baseline_samples"]:
        print(f"  Baseline sample: {sample['baseline_id']} | uid={sample['uid']}")
        for record in sample["analytical_records"]:
            print(
                f"    Record: {record['record_id']} | status={record['recovery_status']} "
                f"| candidates={record['candidate_count']} | uid={record['uid']}"
            )


def print_backward(record_id: str) -> None:
    """Show record-to-candidate-sample tracing for each status type."""
    result = backward_trace(record_id)
    print(f"\nBackward trace for {record_id}")
    print("=" * 60)
    print(f"Record : {result['record']['record_id']} | uid={result['record']['uid']}")
    print(f"Status : {result['status']}")
    if result["failure_reason"]:
        print(f"Failure: {result['failure_reason']}")

    if not result["trace"]:
        print("Trace  : none")
        return

    for item in result["trace"]:
        sample = item["baseline_sample"]
        outcrop = item["outcrop"]
        print(f"Sample : {sample['baseline_id']} | uid={sample['uid']}")
        print(f"Outcrop: {outcrop['outcrop_id']} | uid={outcrop['uid']}")


def main() -> None:
    """Run forward and backward provenance tracing examples."""
    print_forward()
    print_backward("AR002")
    print_backward("AR003")
    print_backward("AR005")


if __name__ == "__main__":
    main()
