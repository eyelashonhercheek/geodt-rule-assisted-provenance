from __future__ import annotations

from typing import List

from src.association.matcher import match_sample_to_outcrops


def association_example_lines(sample_id: str) -> List[str]:
    results = match_sample_to_outcrops(sample_id)
    lines = [f"Association demo for sample {sample_id}"]
    for result in results:
        evidence = ", ".join(result["evidence"]) or "no rule fired"
        lines.append(
            f"- {result['candidate_outcrop_id']} ({result['candidate_name']}): "
            f"score={result['score']:.2f}, candidate={result['is_candidate']}, unresolved={result['unresolved']}, "
            f"ground_truth={result['ground_truth_match']}, evidence=[{evidence}]"
        )
    return lines
