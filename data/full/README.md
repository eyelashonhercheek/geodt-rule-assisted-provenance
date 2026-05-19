# Full Data Release

These files are the full tabular data package for the C&G manuscript
reproducibility revision.

## Files

- `baseline_samples.xlsx`: baseline sample space released for candidate recovery.
- `analysis_records_grain_size_full.xlsx`: grain-size analytical records.
- `analysis_records_hyperspectral_full.xlsx`: hyperspectral analytical records.
- `analysis_records_laser_full.xlsx`: laser analytical records.
- `analysis_records_thin_section_full.xlsx`: thin-section analytical records.
- `analysis_records_xrf_full.xlsx`: XRF analytical records.
- `field_inventory.xlsx`: field inventory and linkage-field documentation.
- `normalization_rules.xlsx`: normalization rules used to standardize identifiers and contextual fields.
- `regenerated_linkage_outputs_CG.xlsx`: regenerated linkage results and summary tables for the manuscript.

## Validation

From the repository root, run:

```bash
python examples/generate_full_linkage.py
python examples/validate_full_release.py
```

The validator checks that:

- the five analytical-record workbooks contain 1400 records in total,
- the baseline workbook contains 100 released baseline samples,
- `linkage_results` contains 1400 rows,
- the full linkage generator reproduces the released `linkage_results` rows,
- summary status counts, report-type counts, failure reasons, evidence coverage,
  candidate distribution, and candidate compression are reproducible from the
  released linkage-result rows.

Expected status counts:

```text
rule-supported link: 440
strong candidate: 123
candidate set: 378
unresolved: 459
```

The workbook stores the equivalent machine-oriented labels as `verified`,
`strong_candidate`, `candidate_level`, and `unresolved`.

## Release Note

The workbook `regenerated_linkage_outputs_CG.xlsx` notes that these regenerated
counts should replace earlier draft counts if the manuscript adopts this full
release package.
