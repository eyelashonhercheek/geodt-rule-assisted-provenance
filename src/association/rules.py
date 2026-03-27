from __future__ import annotations

from typing import Dict, List, Tuple

from src.utils.io_utils import normalize_text


RuleResult = Tuple[float, str]


def identifier_rule(sample: Dict[str, str], outcrop: Dict[str, str]) -> RuleResult:
    if sample["outcrop_id"] == outcrop["outcrop_id"]:
        return 0.45, "high-certainty evidence: sample references the outcrop_id directly"
    return 0.0, ""


def source_rule(sample: Dict[str, str], outcrop: Dict[str, str]) -> RuleResult:
    if normalize_text(sample["source_info"]) == normalize_text(outcrop["region_tag"]):
        return 0.20, "auxiliary evidence: same source or regional grouping"
    return 0.0, ""


def stratigraphy_rule(sample: Dict[str, str], outcrop: Dict[str, str]) -> RuleResult:
    sample_value = normalize_text(sample["stratigraphy"])
    outcrop_value = normalize_text(outcrop["stratigraphy"])
    if sample_value and sample_value == outcrop_value:
        return 0.25, "candidate narrowing: same stratigraphy"
    return 0.0, ""


def lithology_rule(sample: Dict[str, str], outcrop: Dict[str, str]) -> RuleResult:
    sample_value = normalize_text(sample["lithology"])
    outcrop_value = normalize_text(outcrop["lithology"])
    if sample_value and sample_value == outcrop_value:
        return 0.20, "candidate narrowing: same lithology"
    if sample_value and outcrop_value and sample_value.split()[0] == outcrop_value.split()[0]:
        return 0.10, "weak auxiliary evidence: partially compatible lithology"
    return 0.0, ""


def section_rule(sample: Dict[str, str], outcrop: Dict[str, str]) -> RuleResult:
    if normalize_text(sample["section"]) == normalize_text(outcrop["section"]):
        return 0.10, "auxiliary evidence: same section"
    return 0.0, ""


def evaluate_rules(sample: Dict[str, str], outcrop: Dict[str, str]) -> Dict[str, object]:
    evidence: List[str] = []
    total = 0.0

    high_certainty = [identifier_rule(sample, outcrop)]
    auxiliary = [
        source_rule(sample, outcrop),
        section_rule(sample, outcrop),
    ]
    narrowing = [
        stratigraphy_rule(sample, outcrop),
        lithology_rule(sample, outcrop),
    ]

    for score, note in high_certainty + auxiliary + narrowing:
        total += score
        if note:
            evidence.append(note)

    total = round(total, 3)
    is_candidate = total >= 0.45
    unresolved = not is_candidate
    if unresolved:
        evidence.append("unresolved: insufficient combined evidence for confident association")

    return {
        "score": total,
        "evidence": evidence,
        "is_candidate": is_candidate,
        "unresolved": unresolved,
    }
