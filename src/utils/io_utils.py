from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return repo_root() / "data"


def load_csv(name: str) -> List[Dict[str, str]]:
    path = data_dir() / name
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def index_by(rows: Iterable[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    return {row[key]: row for row in rows}


def group_by(rows: Iterable[Dict[str, str]], key: str) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row[key], []).append(row)
    return grouped


def normalize_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())
