# Paper Demo Repository

This repository provides a minimal, auditable reference implementation of the provenance recovery workflow described in the paper.

It demonstrates how fragmented analytical records are reassociated with a baseline sample space through evidence operators, conservative fallback, hierarchical status assignment, and provenance queries over recovered association-layer outputs.

The demo is not a machine-learning model, not a weighted prediction model, and not a simplified copy of the production Vue/Cesium system. It only preserves the method-relevant workflow used in the paper.

## Workflow

```text
analytical record
-> evidence operators
-> candidate baseline samples
-> conservative fallback
-> hierarchical status assignment
-> association-layer output
-> forward/backward provenance tracing
```

## What Is Included

- Small anonymous CSV demo datasets.
- UID generation and parsing for outcrop, baseline sample, and analytical record objects.
- Evidence operators for analytical-record-to-baseline-sample recovery.
- Conservative fallback and hierarchical status assignment.
- Forward and backward provenance queries over recovered association-layer outputs.
- Expected-result validation for the demo records.

## Repository Structure

```text
paper_demo_repo/
├── README.md
├── LICENSE
├── requirements.txt
├── data/
│   ├── outcrops_demo.csv
│   ├── baseline_samples_demo.csv
│   ├── analytical_records_demo.csv
│   ├── expected_linkage_results_demo.csv
│   └── README.md
├── src/
│   ├── uid/
│   │   ├── uid_generator.py
│   │   └── uid_parser.py
│   ├── association/
│   │   ├── evidence_operators.py
│   │   ├── fallback.py
│   │   ├── status.py
│   │   ├── recovery.py
│   │   ├── matcher.py
│   │   └── examples.py
│   ├── provenance/
│   │   ├── forward_query.py
│   │   └── backward_trace.py
│   └── utils/
│       └── io_utils.py
└── examples/
    ├── run_uid_demo.py
    ├── run_recovery_demo.py
    ├── run_association_demo.py
    ├── run_provenance_demo.py
    └── validate_expected_results.py
```

`run_association_demo.py` is retained only as a backward-compatible entry point and calls the recovery workflow internally. The recommended method demo is `run_recovery_demo.py`.

## Quick Start

Use Python 3.10+. No external dependencies are required.

```bash
python examples/run_uid_demo.py
python examples/run_recovery_demo.py
python examples/run_provenance_demo.py
python examples/validate_expected_results.py
```

## Data Model

- `outcrops_demo.csv`: outcrop-level provenance anchors.
- `baseline_samples_demo.csv`: the baseline sample space, used as the reference sample space for recovery.
- `analytical_records_demo.csv`: fragmented target records whose provenance needs to be recovered.
- `expected_linkage_results_demo.csv`: expected status, candidates, and failure reason for validation.

Analytical measurement values are not used as matching evidence in this demo.

## Association Module

The association module is the method core:

- `F_id`: candidate generation from `sample_id_norm`.
- `F_src`: candidate generation from `outcrop_norm` or `section_norm`.
- `F_strat`: candidate generation or constraint from `strat_unit_norm`.
- `F_lith`: weak lithology support over retained candidates.

Evidence operators return candidate sets and evidence logs. They do not make numeric predictions.

## Conservative Fallback

When weak evidence would remove every retained candidate, the workflow keeps the previous candidate set and records:

```text
weak_evidence_should_not_clear_candidates
```

This preserves auditable candidates for manual review.

## Status Assignment

The final recovery status is assigned from retained candidates and evidence conditions:

- `rule-supported link`: one candidate retained by high-confidence identifier evidence with no conflict.
- `strong candidate`: one unique candidate that requires manual confirmation before being used as a definitive link.
- `candidate set`: multiple auditable candidates remain.
- `unresolved`: no reliable candidate is formed under the current baseline sample space or available fields.

Unresolved records include a `failure_reason`: `outside_baseline`, `missing_source`, `missing_source_and_stratigraphy`, or `no_reliable_candidate`.

## Provenance Queries

Forward query:

```text
outcrop -> recovered baseline samples -> analytical records linked by recovery results
```

Backward trace:

```text
analytical record -> recovered candidate sample(s) -> outcrop
```

A `candidate set` returns multiple possible traces. An `unresolved` record returns its status and failure reason without forcing a provenance chain.

## Expected Demo Cases

- `AR001`: `rule-supported link`
- `AR002`: `strong candidate`
- `AR003`: `candidate set`
- `AR004`: conservative fallback case
- `AR005`: `unresolved` / `outside_baseline`
- `AR006`: `unresolved` / `missing_source_and_stratigraphy`
- `AR007`: `unresolved` / `missing_source`

## Notes

- The demo data are anonymized and simplified.
- Coordinates, names, and identifiers are illustrative.
- No database connection, API key, token, private dataset, or UI dependency is included.
