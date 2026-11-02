# Auditable Cross-Scale Provenance Recovery

## Major revision evaluation: package v1.1.0, 2 November 2026

The revised evaluation is in [`revision_20261102/`](revision_20261102/).
It includes the registered D3 inputs, fixed engine 0.4-r5, twelve configurations,
16,800 prediction rows, 429 documentary development relationships, 89 anonymized
human source-page review records, six original source reports and file hashes.

The D3 full workflow yields **52 / 396 / 374 / 578** records in its four states,
with 822 nonempty outputs and 7,031 candidate edges. All 52 current accepted
associations are supported in the reviewed census (laser 3, thin-section 5,
grain-size 44). Hyperspectral and XRF records enter the other-state and diagnostic
review checks. Across the 71 supported review targets, 69 remain in the final
candidates; eighteen other reviewed records remain unconfirmed. Review scope,
selection arms and code-dependent interpretations are retained in the ledger.

These results use a different policy from the historical 440 / 123 / 378 / 459
release preserved below. Candidate relationships, documentary interpretations
and finer physical-sample allocations retain their stated evidence scopes.

### Quick check for the revised manuscript

Python 3.10 or later is sufficient for these standard-library checks:

```bash
cd revision_20261102
python -B support/reproducibility/test_r5.py
python -B support/reproducibility/reproduce_review_sampling.py
python -B support/reproducibility/reproduce_review89.py
python -B support/reproducibility/analyze_R25_pairs.py
python -B support/reproducibility/audit_R25_1.py
python -B support/reproducibility/summarize_review_by_type.py --output-dir review_type_summary
```

See the [versioned README](revision_20261102/README.md) for full replay commands,
optional PDF replay dependencies and expected outputs. Run commands that regenerate
tables on a working copy. The input and review tables remain registered read-only
evidence. All original report locators distinguish physical pages from report pages.

### Historical direct-link replay

The supplementary historical replay recovers the original format-only ID/source
rule and reproduces 261 direct links: 94 laser, 80 thin-section and 87 grain-size.
It is separate from the revised acceptance policy and from the later 543-query
identifier-candidate scenario. The historical 50-case roster is retained with its
recorded provenance; the revised human validation uses the completed 89-case review.

### Archived historical version

The DOI below identifies the historical v1.0.2 archive. The revised files must be
archived as a new Zenodo version before that new version DOI is used in a citation.
The existing DOI remains available for reproduction of the earlier release.

## Historical demonstration and tabular release

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20281183.svg)](https://doi.org/10.5281/zenodo.20281183)

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
rule-supported link: 440
strong candidate: 123
candidate set: 378
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

The released workbook stores machine-oriented status labels
(`verified`, `strong_candidate`, `candidate_level`, `unresolved`). The validation
scripts print the manuscript-facing labels (`rule-supported link`, `strong
candidate`, `candidate set`, `unresolved`) so the command-line output matches the
paper tables.

The full-release workbook states that the regenerated deterministic run should
replace earlier draft counts if the manuscript adopts this release.

## Data and Code License

The code is released under the MIT License. The released tabular data are
intended for public archival release with a CC BY 4.0-compatible data license.
Please cite the archived release DOI rather than only the GitHub repository:
https://doi.org/10.5281/zenodo.20281183
