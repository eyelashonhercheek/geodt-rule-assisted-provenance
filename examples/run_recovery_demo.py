from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.association.examples import recovery_example_lines


def main() -> None:
    """Print recovery status, candidates, evidence logs, and fallback details."""
    for record_id in ("AR001", "AR002", "AR003", "AR004", "AR005", "AR006", "AR007"):
        print("\n".join(recovery_example_lines(record_id)))
        print("=" * 60)


if __name__ == "__main__":
    main()
