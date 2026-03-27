from __future__ import annotations

from typing import Dict, List

from src.association.rules import evaluate_rules
from src.utils.io_utils import load_csv


def match_sample_to_outcrops(sample_id: str) -> List[Dict[str, object]]:
    samples = load_csv("samples_demo.csv")
    outcrops = load_csv("outcrops_demo.csv")

    sample = next((row for row in samples if row["sample_id"] == sample_id), None)
    if sample is None:
        raise ValueError(f"Unknown sample_id: {sample_id}")

    ranked: List[Dict[str, object]] = []
    for outcrop in outcrops:
        result = evaluate_rules(sample, outcrop)
        ranked.append(
            {
                "sample_id": sample_id,
                "candidate_outcrop_id": outcrop["outcrop_id"],
                "candidate_name": outcrop["outcrop_name"],
                "score": result["score"],
                "is_candidate": result["is_candidate"],
                "unresolved": result["unresolved"],
                "evidence": result["evidence"],
                "ground_truth_match": sample["outcrop_id"] == outcrop["outcrop_id"],
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
