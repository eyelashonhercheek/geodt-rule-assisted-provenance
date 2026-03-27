from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.association.examples import association_example_lines


def main() -> None:
    print("\n".join(association_example_lines("SP001")))


if __name__ == "__main__":
    main()
