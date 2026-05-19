# Data Directory

This directory contains the data needed to inspect and validate the provenance
recovery workflow.

## Demo CSV Files

The CSV files in this folder are small anonymous examples for method inspection:

- `outcrops_demo.csv`: outcrop-level provenance anchors.
- `baseline_samples_demo.csv`: the reference sample space used for candidate recovery.
- `analytical_records_demo.csv`: fragmented analytical records to be reassociated.
- `expected_linkage_results_demo.csv`: expected status and candidate outcomes for the demo records.

Run:

```bash
python examples/validate_expected_results.py
```

## Full Release Files

The `full/` folder contains the complete tabular release used for manuscript
result validation:

- five analytical-record workbooks,
- one baseline-sample workbook,
- the field inventory,
- normalization rules,
- regenerated linkage outputs and summary sheets.

Run:

```bash
python examples/generate_full_linkage.py
python examples/validate_full_release.py
```

`generate_full_linkage.py` regenerates the released linkage rows from the full
input workbooks and verifies that they match the published `linkage_results`
sheet. The analytical measurement values are not used as matching evidence. The
workflow uses identifier, source or section, stratigraphic, and lithological
fields to generate candidates, apply conservative fallback, assign statuses, and
produce traceable association-layer outputs.
