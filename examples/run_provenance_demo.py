from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.provenance.backward_trace import backward_trace
from src.provenance.forward_query import forward_query


def print_forward() -> None:
    result = forward_query("OC001")
    print("Forward provenance demo")
    print("=" * 60)
    print(f"Outcrop: {result['outcrop']['outcrop_id']} | uid={result['outcrop']['uid']}")
    for sample in result["samples"]:
        print(f"  Sample: {sample['sample_id']} | uid={sample['uid']}")
        for record in sample["analytical_records"]:
            print(f"    Record: {record['record_id']} | uid={record['uid']} | type={record['analysis_type']}")


def print_backward() -> None:
    result = backward_trace("AR002")
    print("\nBackward provenance demo")
    print("=" * 60)
    print(f"Record : {result['record']['record_id']} | uid={result['record']['uid']}")
    print(f"Sample : {result['sample']['sample_id']} | uid={result['sample']['uid']}")
    print(f"Outcrop: {result['outcrop']['outcrop_id']} | uid={result['outcrop']['uid']}")


def main() -> None:
    print_forward()
    print_backward()


if __name__ == "__main__":
    main()
