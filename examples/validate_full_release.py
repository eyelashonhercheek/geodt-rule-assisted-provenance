from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.xlsx_utils import find_header_row, load_xlsx_rows, rows_to_dicts
from examples.generate_full_linkage import generate_rows


FULL_DATA_DIR = ROOT / "data" / "full"

ANALYSIS_FILES = {
    "analysis_records_grain_size_full.xlsx": 200,
    "analysis_records_hyperspectral_full.xlsx": 300,
    "analysis_records_laser_full.xlsx": 400,
    "analysis_records_thin_section_full.xlsx": 200,
    "analysis_records_xrf_full.xlsx": 300,
}

OUTPUT_FILE = "regenerated_linkage_outputs_CG.xlsx"
STATUS_ORDER = ["verified", "strong_candidate", "candidate_level", "unresolved"]


def as_int(value: str) -> int:
    return int(float(value or 0))


def as_float(value: str) -> float:
    return float(value or 0)


def approx_equal(actual: float, expected: float, tolerance: float = 0.02) -> bool:
    return abs(actual - expected) <= tolerance


def load_table(file_name: str, sheet_name: str | None = None, header: str | None = None):
    rows = load_xlsx_rows(FULL_DATA_DIR / file_name, sheet_name=sheet_name)
    header_row = find_header_row(rows, header) if header else 0
    return rows_to_dicts(rows, header_row=header_row)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def validate_input_inventory(failures: list[str]) -> tuple[int, int]:
    total_records = 0
    for file_name, expected_count in ANALYSIS_FILES.items():
        rows = load_table(file_name)
        total_records += len(rows)
        require(
            len(rows) == expected_count,
            f"{file_name}: expected {expected_count} records, found {len(rows)}",
            failures,
        )

    baseline = load_table("baseline_samples.xlsx", header="baseline_id")
    baseline_records = [row for row in baseline if row.get("baseline_id", "").startswith("BS")]
    require(
        total_records == 1400,
        f"analysis inventory: expected 1400 records, found {total_records}",
        failures,
    )
    require(
        len(baseline_records) >= 100,
        f"baseline inventory: expected at least 100 baseline samples, found {len(baseline_records)}",
        failures,
    )
    return total_records, len(baseline_records)


def validate_status_summary(linkage_rows, failures: list[str]) -> None:
    status_counts = Counter(row["final_status"] for row in linkage_rows)
    summary_rows = load_table(OUTPUT_FILE, "summary_status")
    for row in summary_rows:
        status = row["status"]
        if status not in STATUS_ORDER:
            continue
        expected_count = as_int(row["count"])
        actual_count = status_counts[status]
        require(
            actual_count == expected_count,
            f"summary_status[{status}]: expected {expected_count}, computed {actual_count}",
            failures,
        )


def validate_by_report_type(linkage_rows, failures: list[str]) -> None:
    grouped = defaultdict(Counter)
    for row in linkage_rows:
        grouped[row["source_type"]][row["final_status"]] += 1
        grouped[row["source_type"]]["total"] += 1

    for row in load_table(OUTPUT_FILE, "by_report_type"):
        source_type = row["source_type"]
        for key in ["total", *STATUS_ORDER]:
            expected = as_int(row[key])
            actual = grouped[source_type][key]
            require(
                actual == expected,
                f"by_report_type[{source_type}][{key}]: expected {expected}, computed {actual}",
                failures,
            )


def validate_failure_reasons(linkage_rows, failures: list[str]) -> None:
    unresolved = [row for row in linkage_rows if row["final_status"] == "unresolved"]
    reason_counts = Counter(row["failure_reason"] for row in unresolved)
    for row in load_table(OUTPUT_FILE, "failure_reasons"):
        reason = row["failure_reason"]
        expected = as_int(row["record_count"])
        actual = reason_counts[reason]
        require(
            actual == expected,
            f"failure_reasons[{reason}]: expected {expected}, computed {actual}",
            failures,
        )


def distribution_bucket(candidate_count: int) -> str:
    if candidate_count == 0:
        return "|C_f|=0"
    if candidate_count == 1:
        return "|C_f|=1"
    if 2 <= candidate_count <= 5:
        return "2≤|C_f|≤5"
    if 6 <= candidate_count <= 10:
        return "6≤|C_f|≤10"
    return "|C_f|>10"


def validate_candidate_distribution(linkage_rows, failures: list[str]) -> None:
    buckets = Counter(distribution_bucket(as_int(row["final_candidate_count"])) for row in linkage_rows)
    positive_counts = [
        as_int(row["final_candidate_count"])
        for row in linkage_rows
        if as_int(row["final_candidate_count"]) > 0
    ]
    for row in load_table(OUTPUT_FILE, "candidate_distribution"):
        label = row["final_candidate_count_range"]
        if label == "positive_candidate_average":
            actual_average = sum(positive_counts) / len(positive_counts)
            require(
                approx_equal(actual_average, as_float(row["record_count"])),
                f"candidate_distribution[{label}]: expected {row['record_count']}, computed {actual_average:.2f}",
                failures,
            )
        elif label == "positive_candidate_median":
            sorted_counts = sorted(positive_counts)
            midpoint = len(sorted_counts) // 2
            actual_median = sorted_counts[midpoint]
            require(
                approx_equal(actual_median, as_float(row["record_count"])),
                f"candidate_distribution[{label}]: expected {row['record_count']}, computed {actual_median:.2f}",
                failures,
            )
        else:
            expected = as_int(row["record_count"])
            actual = buckets[label]
            require(
                actual == expected,
                f"candidate_distribution[{label}]: expected {expected}, computed {actual}",
                failures,
            )


def validate_evidence_coverage(linkage_rows, failures: list[str]) -> None:
    field_by_layer = {
        "S1 样号候选层": "id_candidate_count",
        "S2 来源/剖面候选层": "source_candidate_count",
        "S3 地层候选层": "strat_candidate_count",
        "S4 岩性支持层": "lithology_candidate_count",
        "S5 完整工作流": "final_candidate_count",
    }
    for row in load_table(OUTPUT_FILE, "evidence_coverage"):
        layer = row["evidence_layer"]
        field = field_by_layer[layer]
        actual = sum(1 for item in linkage_rows if as_int(item[field]) > 0)
        expected = as_int(row["records_with_at_least_one_candidate"])
        require(
            actual == expected,
            f"evidence_coverage[{layer}]: expected {expected}, computed {actual}",
            failures,
        )


def validate_candidate_compression(linkage_rows, failures: list[str]) -> None:
    field_by_layer = {
        "S1 样号候选层": "id_candidate_count",
        "S2 来源/剖面候选层": "source_candidate_count",
        "S3 地层候选层": "strat_candidate_count",
        "S4 岩性支持层": "lithology_candidate_count",
        "S5 完整工作流": "final_candidate_count",
        "S5 最终候选层": "final_candidate_count",
    }
    total = len(linkage_rows)
    for row in load_table(OUTPUT_FILE, "candidate_compression"):
        layer = row["layer"]
        if layer == "S0 初始基准空间":
            continue
        field = field_by_layer[layer]
        values = sorted(as_int(item[field]) for item in linkage_rows)
        average = sum(values) / total
        median = (values[total // 2 - 1] + values[total // 2]) / 2
        require(
            approx_equal(average, as_float(row["average_candidate_count_all_records"])),
            f"candidate_compression[{layer}] average: expected {row['average_candidate_count_all_records']}, computed {average:.2f}",
            failures,
        )
        require(
            approx_equal(median, as_float(row["median_candidate_count_all_records"])),
            f"candidate_compression[{layer}] median: expected {row['median_candidate_count_all_records']}, computed {median:.2f}",
            failures,
        )


def main() -> None:
    failures: list[str] = []
    input_total, baseline_total = validate_input_inventory(failures)
    linkage_rows = load_table(OUTPUT_FILE, "linkage_results")
    generated_rows = generate_rows()

    require(
        len(linkage_rows) == input_total,
        f"linkage_results: expected {input_total} rows from input records, found {len(linkage_rows)}",
        failures,
    )
    require(
        generated_rows == linkage_rows,
        "linkage_results: generated full linkage rows do not match the released workbook",
        failures,
    )

    validate_status_summary(linkage_rows, failures)
    validate_by_report_type(linkage_rows, failures)
    validate_failure_reasons(linkage_rows, failures)
    validate_candidate_distribution(linkage_rows, failures)
    validate_evidence_coverage(linkage_rows, failures)
    validate_candidate_compression(linkage_rows, failures)

    if failures:
        print("Full-release validation failed")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    status_counts = Counter(row["final_status"] for row in linkage_rows)
    print("Full-release validation passed.")
    print(f"Input analytical records: {input_total}")
    print(f"Baseline samples released: {baseline_total}")
    print(f"Linkage result rows: {len(linkage_rows)}")
    for status in STATUS_ORDER:
        print(f"{status}: {status_counts[status]}")


if __name__ == "__main__":
    main()
