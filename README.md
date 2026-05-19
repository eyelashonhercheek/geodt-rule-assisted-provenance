# Auditable Cross-Scale Provenance Recovery Demo

This repository provides a reproducible reference implementation and release
package for the provenance recovery workflow described in the manuscript:

> An Auditable Cross-Scale Provenance Recovery Framework for Fragmented Geological Records

The repository contains two reproducibility layers:

- `data/*_demo.csv`: a small anonymous demo dataset used to inspect the method logic record by record.
- `data/full/*.xlsx`: the full release package used to validate the manuscript-level results.

The code is not a machine-learning model and does not use measurement values as
matching evidence. It implements deterministic evidence operators, conservative
fallback, hierarchical status assignment, and provenance queries over recovered
association-layer outputs.

## Quick Start

Use Python 3.10 or later.

```bash
python examples/run_uid_demo.py
python examples/run_recovery_demo.py
python examples/run_provenance_demo.py
python examples/validate_expected_results.py
python examples/generate_full_linkage.py
python examples/validate_full_release.py
```

No third-party Python package is required. The full-release validator reads the
published `.xlsx` files with the Python standard library.

Expected full-release validation output:

```text
Full-release validation passed.
Input analytical records: 1400
Baseline samples released: 100
Linkage result rows: 1400
verified: 440
strong_candidate: 123
candidate_level: 378
unresolved: 459
```

## Repository Structure

```text
paper_demo_repo/
  README.md
  LICENSE
  requirements.txt
  data/
    README.md
    full/
      README.md
      analysis_records_grain_size_full.xlsx
      analysis_records_hyperspectral_full.xlsx
      analysis_records_laser_full.xlsx
      analysis_records_thin_section_full.xlsx
      analysis_records_xrf_full.xlsx
      baseline_samples.xlsx
      field_inventory.xlsx
      normalization_rules.xlsx
      regenerated_linkage_outputs_CG.xlsx
    analytical_records_demo.csv
    baseline_samples_demo.csv
    expected_linkage_results_demo.csv
    outcrops_demo.csv
  src/
    uid/
    association/
    provenance/
    utils/
  examples/
    run_uid_demo.py
    run_recovery_demo.py
    run_association_demo.py
    run_provenance_demo.py
    validate_expected_results.py
    validate_full_release.py
```

## Method Workflow

```text
analytical record
-> evidence operators
-> candidate baseline samples
-> conservative fallback
-> hierarchical status assignment
-> association-layer output
-> forward/backward provenance tracing
```

Evidence operators:

- `F_id`: candidate generation from normalized sample identifiers.
- `F_src`: candidate generation from normalized outcrop or section fields.
- `F_strat`: candidate generation or constraint from normalized stratigraphic fields.
- `F_lith`: weak lithology support over retained candidates.

Conservative fallback preserves auditable candidates when weak evidence would
erase all retained candidates.

## Full Data Validation

`examples/generate_full_linkage.py` regenerates the 1400-row full linkage table
from the released baseline and analytical-record workbooks, then compares the
generated rows against the `linkage_results` sheet in
`regenerated_linkage_outputs_CG.xlsx`.

`examples/validate_full_release.py` runs the full linkage generator and checks
that the released full data package is internally consistent with the
manuscript-level results:

- 1400 analytical records are present across five analytical report tables.
- 100 baseline samples are present in the released baseline table.
- 1400 linkage-result rows are present.
- Regenerated linkage rows match the released `linkage_results` sheet.
- Status counts, report-type counts, failure reasons, evidence coverage,
  candidate distribution, and candidate compression summaries are recomputed
  from `linkage_results` and compared against the published summary sheets.

The full-release workbook states that the regenerated deterministic run should
replace earlier draft counts if the manuscript adopts this release.

## Data and Code License

The code is released under the MIT License. The released tabular data are
intended for public archival release with a CC BY 4.0-compatible data license.
When a DOI is minted, cite the archived dataset rather than only the GitHub
repository.
