from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.xlsx_utils import find_header_row, load_xlsx_rows, rows_to_dicts


FULL_DATA_DIR = ROOT / "data" / "full"
EXPECTED_OUTPUT = "regenerated_linkage_outputs_CG.xlsx"

ANALYSIS_FILES = [
    "analysis_records_hyperspectral_full.xlsx",
    "analysis_records_xrf_full.xlsx",
    "analysis_records_laser_full.xlsx",
    "analysis_records_thin_section_full.xlsx",
    "analysis_records_grain_size_full.xlsx",
]

SOURCE_TYPE_LABELS = {
    "高光谱矿物分析报告": "高光谱矿物分析报告",
    "XRF矿物分析": "XRF测试报告",
    "激光测试与分析": "激光测试与分析报告",
    "岩石薄片分析": "岩石薄片分析报告",
    "岩石粒度分析": "岩石粒度分析报告",
}

OUTPUT_COLUMNS = [
    "record_id",
    "source_type",
    "sample_id_raw",
    "sample_id_norm",
    "canon_sample_id",
    "section_num",
    "strat_group",
    "outcrop_cat",
    "id_candidate_count",
    "source_candidate_count",
    "strat_candidate_count",
    "lithology_candidate_count",
    "final_candidate_count",
    "final_status",
    "matched_baseline_id",
    "candidate_baseline_ids",
    "needs_manual_confirmation",
    "evidence_used",
    "failure_reason",
    "notes",
]


def load_table(file_name: str, sheet_name: str | None = None, header: str | None = None):
    rows = load_xlsx_rows(FULL_DATA_DIR / file_name, sheet_name=sheet_name)
    header_row = find_header_row(rows, header) if header else 0
    return rows_to_dicts(rows, header_row=header_row)


def clean(value: str) -> str:
    return (
        (value or "")
        .replace(" ", "")
        .replace("\u3000", "")
        .replace("‐", "-")
        .replace("–", "-")
        .replace("—", "-")
        .strip()
    )


def is_missing(value: str) -> bool:
    return clean(value).upper() in {"", "NA", "NAN", "NONE"}


def strat_group(value: str, fallback_sample_id: str = "") -> str:
    value = clean(value)
    if is_missing(value):
        value = clean(fallback_sample_id)
    match = re.match(r"长(\d)", value)
    if match:
        return f"长{match.group(1)}"
    return value


def canonical_sample_id(row: dict[str, str]) -> str:
    sample_id = clean(row.get("sample_id_norm") or row.get("sample_id_raw") or "")
    strat = clean(row.get("strat_unit_norm", ""))

    if re.fullmatch(r"\d+", sample_id) and re.match(r"长\d+", strat):
        return f"{strat}-{sample_id}"

    sample_id = re.sub(r"^\d+-", "", sample_id)
    sample_id = re.sub(r"^C(?=\d)", "长", sample_id)
    return sample_id


def section_num(row: dict[str, str], canon_id: str) -> str:
    sample_id = clean(row.get("sample_id_norm") or row.get("sample_id_raw") or "")
    if re.fullmatch(r"\d+", sample_id) and re.match(r"长\d+", clean(row.get("strat_unit_norm", ""))):
        return sample_id
    match = re.match(r"^(\d+)-", sample_id)
    if match:
        return match.group(1)

    for field in ("section_norm", "outcrop_norm", "outcrop_raw", "section_raw"):
        value = clean(row.get(field, ""))
        if is_missing(value):
            continue
        if value.isdigit():
            return value
        match = re.search(r"延河(\d+)号?", value)
        if match:
            return match.group(1)
        match = re.fullmatch(r"(\d+)号", value)
        if match:
            return match.group(1)
    return ""


def outcrop_category(row: dict[str, str], section: str, canon_id: str) -> str:
    values = [clean(row.get(key, "")) for key in ("outcrop_norm", "outcrop_raw", "section_norm", "section_raw")]
    if any("八道湾" in value for value in values):
        return "八道湾"
    if any("延河" in value for value in values):
        return "延河"
    if section and canon_id.startswith("长"):
        return "延河"
    return ""


def has_sandstone_support(lithology: str) -> bool:
    lithology = clean(lithology)
    return "砂岩" in lithology or "粉砂岩" in lithology


def sorted_ids(rows: list[dict[str, str]]) -> list[str]:
    return sorted(row["baseline_id"] for row in rows)


def semicolon(ids: list[str]) -> str:
    return ";".join(ids)


def status_for_candidates(candidate_ids: list[str], evidence_used: str) -> str:
    if not candidate_ids:
        return "unresolved"
    if evidence_used == "id+section" and len(candidate_ids) == 1:
        return "verified"
    if len(candidate_ids) == 1:
        return "strong_candidate"
    return "candidate_level"


def failure_reason(row: dict[str, str], candidates: list[str], source_candidates: list[str], strat_candidates: list[str]) -> str:
    if candidates:
        return "over_ambiguous" if len(candidates) > 10 else ""
    has_source = bool(source_candidates)
    has_strat_field = not is_missing(row.get("strat_unit_norm", ""))
    has_strat = bool(strat_candidates)
    if has_source or has_strat:
        return "outside_baseline"
    if clean(row.get("has_outcrop", "")).upper() == "Y":
        return "outside_baseline"
    if has_strat_field:
        return "missing_source"
    return "missing_source_and_stratigraphy"


def generate_rows() -> list[dict[str, str]]:
    baseline_rows = [
        row
        for row in load_table("baseline_samples.xlsx", header="baseline_id")
        if row.get("baseline_id", "").startswith("BS")
    ]

    baseline_by_id = defaultdict(list)
    baseline_by_source = defaultdict(list)
    baseline_by_outcrop = defaultdict(list)
    baseline_by_strat = defaultdict(list)
    for sample in baseline_rows:
        sample["section_group"] = "" if is_missing(sample.get("section_norm", "")) else clean(sample.get("section_norm", ""))
        sample["outcrop_group"] = "八道湾" if clean(sample.get("outcrop_norm", "")) == "八道湾" else clean(sample.get("outcrop_norm", ""))
        sample["strat_group"] = strat_group(sample.get("strat_unit_norm", ""))
        baseline_by_id[clean(sample.get("sample_id_norm", ""))].append(sample)
        baseline_by_source[(sample["outcrop_group"], sample["section_group"])].append(sample)
        baseline_by_outcrop[sample["outcrop_group"]].append(sample)
        baseline_by_strat[sample["strat_group"]].append(sample)

    generated: list[dict[str, str]] = []
    for file_name in ANALYSIS_FILES:
        for row in load_table(file_name):
            canon_id = canonical_sample_id(row)
            section = section_num(row, canon_id)
            outcrop = outcrop_category(row, section, canon_id)
            group = strat_group(row.get("strat_unit_norm", ""), canon_id)

            id_candidates = sorted_ids(baseline_by_id.get(canon_id, []))
            if outcrop and section:
                source_candidates = sorted_ids(baseline_by_source.get((outcrop, section), []))
            elif outcrop:
                source_candidates = sorted_ids(baseline_by_outcrop.get(outcrop, []))
            else:
                source_candidates = []
            strat_candidates = sorted_ids(baseline_by_strat.get(group, [])) if group else []
            lithology_count = 99 if has_sandstone_support(row.get("lithology_norm", "")) else 0

            evidence_used = ""
            final_candidates: list[str] = []
            id_candidate_count = len(id_candidates)
            if id_candidates:
                matching_section = [
                    sample["baseline_id"]
                    for sample in baseline_by_id[canon_id]
                    if section and sample["section_group"] == section
                ]
                if not matching_section and not section and outcrop:
                    matching_section = [
                        sample["baseline_id"]
                        for sample in baseline_by_id[canon_id]
                        if sample["outcrop_group"] == outcrop
                    ]
                if matching_section:
                    final_candidates = sorted(matching_section)
                    id_candidate_count = len(final_candidates)
                    evidence_used = "id+section"
                else:
                    final_candidates = id_candidates
                    evidence_used = "id_only"
            elif source_candidates and strat_candidates:
                intersection = sorted(set(source_candidates) & set(strat_candidates))
                if intersection:
                    final_candidates = intersection
                    evidence_used = "source+strat"
                else:
                    final_candidates = source_candidates
                    evidence_used = "source_fallback"
            elif source_candidates:
                final_candidates = source_candidates
                evidence_used = "source_fallback"
            elif strat_candidates:
                final_candidates = strat_candidates
                evidence_used = "strat"
            else:
                final_candidates = []
                evidence_used = "strat_fallback" if outcrop or section else "strat"

            status = status_for_candidates(final_candidates, evidence_used)
            reason = failure_reason(row, final_candidates, source_candidates, strat_candidates)
            generated.append(
                {
                    "record_id": row["record_id"],
                    "source_type": SOURCE_TYPE_LABELS.get(row["source_type"], row["source_type"]),
                    "sample_id_raw": row["sample_id_raw"],
                    "sample_id_norm": row["sample_id_norm"],
                    "canon_sample_id": canon_id,
                    "section_num": section,
                    "strat_group": group,
                    "outcrop_cat": outcrop,
                    "id_candidate_count": str(id_candidate_count),
                    "source_candidate_count": str(len(source_candidates)),
                    "strat_candidate_count": str(len(strat_candidates)),
                    "lithology_candidate_count": str(lithology_count),
                    "final_candidate_count": str(len(final_candidates)),
                    "final_status": status,
                    "matched_baseline_id": final_candidates[0] if status in {"verified", "strong_candidate"} else "",
                    "candidate_baseline_ids": semicolon(final_candidates),
                    "needs_manual_confirmation": "N" if status == "verified" else "Y",
                    "evidence_used": evidence_used,
                    "failure_reason": reason,
                    "notes": row.get("notes", ""),
                }
            )
    return generated


def compare_with_expected(generated: list[dict[str, str]]) -> list[str]:
    expected = load_table(EXPECTED_OUTPUT, "linkage_results")
    failures: list[str] = []
    if len(generated) != len(expected):
        failures.append(f"row count mismatch: generated {len(generated)}, expected {len(expected)}")
        return failures

    for index, (actual, target) in enumerate(zip(generated, expected), start=1):
        for column in OUTPUT_COLUMNS:
            if actual[column] != target[column]:
                failures.append(
                    f"row {index} {actual['record_id']} column {column}: "
                    f"generated {actual[column]!r}, expected {target[column]!r}"
                )
                if len(failures) >= 25:
                    return failures
    return failures


def main() -> None:
    generated = generate_rows()
    failures = compare_with_expected(generated)
    status_counts = Counter(row["final_status"] for row in generated)

    if failures:
        print("Full linkage generation differed from the released workbook.")
        for failure in failures:
            print(f"- {failure}")
        print("Generated status counts:")
        for status in ("verified", "strong_candidate", "candidate_level", "unresolved"):
            print(f"{status}: {status_counts[status]}")
        raise SystemExit(1)

    print("Full linkage generation matched the released workbook.")
    print(f"Generated linkage rows: {len(generated)}")
    for status in ("verified", "strong_candidate", "candidate_level", "unresolved"):
        print(f"{status}: {status_counts[status]}")


if __name__ == "__main__":
    main()
