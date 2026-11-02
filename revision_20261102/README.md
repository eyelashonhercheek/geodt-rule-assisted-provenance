# Supplementary reproducibility archive

An Auditable Cross-Scale Provenance Recovery Framework for Fragmented Geological Records

## Contents

- support/Table_S1_human_review89_source_evidence.csv: registered anonymized judgments and source evidence for 89 records.
- support/Table_S1_review_by_report_type.csv: five-type summary regenerated from the same review judgments.
- support/review_by_report_type.json: totals and report-type scope of that summary.
- support/Table_S1_English_index.csv: English presentation index of those same judgments, retaining original Chinese labels and reasons.
- support/Table_S2_human_review89_method_comparison.csv: 48 method-by-review-scope comparison rows.
- support/Table_S3_D3_evidence_strata.csv: development-reference results by evidence stratum.
- support/Table_S4_versions_and_interpretations.md and Table_S5_comparison_protocol.md: version and execution details.
- support/reproducibility/: fixed inputs, engine, predictions, reference targets and analysis scripts.
- support/diagnostics/: source-blocking and operator-order diagnostics.
- support/paired_case_ledger_R25.json: paired retention mechanisms and operator traces. Retained suffixes identify computational versions.
- 原始报告/: six original PDF reports, unchanged. Their filenames match the source-report locators in the review table.
- support/raw_report_file_manifest.json and SHA256_manifest.csv: original-report and complete archive checksums.

## Reproduce the reported comparisons

Use Python 3.10 or later. The following numerical checks use only the Python standard library. Run from the unpacked archive root:

```
python -B support/reproducibility/reproduce_review_sampling.py
python -B support/reproducibility/reproduce_review89.py
python -B support/reproducibility/analyze_R25_pairs.py
python -B support/reproducibility/audit_R25_1.py
python -B support/reproducibility/test_r5.py
python -B support/reproducibility/summarize_review_by_type.py --output-dir review_type_summary
```

The report-type summary reads the unchanged Table S1 and frozen predictions, and writes to a new output directory. The 52 accepted records comprise 3 laser, 5 thin-section and 44 grain-size records; hyperspectral and XRF have no automatic accepts in this run.

Expected review checks: 89 distinct records; 71 supported and 18 unconfirmed; all 52 current accepts supported; 69 of 71 supported targets retained; 48 configuration/scope rows verified. Paired full-versus-strict retention is 383/13/33/0 on 429 development queries and 68/1/2/0 on 71 reviewed positives (both/full-only/strict-only/neither).

To replay all twelve configurations for D2 and D3, run the following on a working copy. This command regenerates comparison CSV/JSON files alongside the inputs:

```
python -B support/reproducibility/run_author_revision_v5.py
python -B support/reproducibility/run_D3_diagnostics.py
```

The D3 full workflow has 52 rule-supported links, 396 strong candidates, 374 candidate sets and 578 unresolved records. Its 822 nonempty outputs contain 7,031 candidate edges. The 429 development targets and 71 reviewed positives are different scopes with overlapping record keys; their denominators are not added. Retrieval baselines output candidate sets and have no automatic-acceptance policy.

## Source locators and evidence

PDF physical pages, printed report pages and directory-referenced report pages are distinct. Hyperspectral/XRF detail pages may lack a visible printed page label. Original source values and reasons are retained in Chinese. The English index translates the structured report-type, judgment and evidence-basis fields; it adds no expert judgment. Review provenance and tool use are described in support/Review_provenance.md and the manuscript.

Historical code/data are available at https://github.com/eyelashonhercheek/geodt-rule-assisted-provenance . The fixed inputs and analysis files in this archive define the revised evaluation.

## Portable input metadata

The public input JSON files replace local-machine path prefixes in the provenance metadata with source basenames. All 100 baseline rows, 1,400 query records and policy fields are unchanged. Metadata_export_manifest.json records the registered source hashes and public-file hashes. SHA256_manifest.csv identifies the files actually supplied in this archive.

## Historical direct-link replay added in this archive

The support/historical_replay directory supplies the recovered 16 April 2026 direct-link rule, its 261-row replay, an 800-record trace, retained input workbooks, historical code sources and separate traces of the 30 inspection records and 20 unresolved-case suggestions. See its README for package versions and execution commands. The current D3 inputs, predictions, 429-reference comparison and 89-record human-review judgments are unchanged.
