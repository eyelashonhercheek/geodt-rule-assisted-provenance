# Paper Demo Repository

This repository is a minimal, open-source companion demo for a paper on a provenance-aware framework for cross-scale geological data organization and rule-assisted association.

It reproduces the core method flow only:

- provenance-aware framework
- cross-scale geological data organization
- UID generation and parsing
- rule-assisted association
- bidirectional provenance
- forward query / backward provenance restoration
- a minimal runnable demonstration

This is not the full production system.

- The original project contains a larger visualization-oriented implementation.
- The full system architecture, full UI, full database services, and full datasets are not included here.
- Sensitive configuration, private data, and heavyweight deployment dependencies are intentionally excluded.

## What Is Included

- small anonymous CSV demo datasets
- pure Python logic for UID generation and parsing
- rule-assisted candidate matching between outcrops and samples
- forward provenance query: `outcrop -> sample -> analytical_record`
- backward provenance restoration: `analytical_record -> sample -> outcrop`

## Repository Structure

```text
paper_demo_repo/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   ├── outcrops_demo.csv
│   ├── samples_demo.csv
│   ├── analytical_records_demo.csv
│   └── README.md
├── src/
│   ├── uid/
│   │   ├── uid_generator.py
│   │   └── uid_parser.py
│   ├── association/
│   │   ├── rules.py
│   │   ├── matcher.py
│   │   └── examples.py
│   ├── provenance/
│   │   ├── forward_query.py
│   │   └── backward_trace.py
│   └── utils/
│       └── io_utils.py
└── examples/
    ├── run_uid_demo.py
    ├── run_association_demo.py
    └── run_provenance_demo.py
```

## Relationship To The Original Project

This demo was distilled from a larger Cesium/Vue geological corridor project. The demo logic was derived from the following kinds of original code:

- GeoJSON feature property usage for object identification
- multi-entity relation querying between outcrops, samples, and records
- relation-table style association modeling
- forward and backward detail retrieval patterns

The code here is rewritten as a minimal, standalone Python demo rather than copied as a UI system.

## Quick Start

Use Python 3.10+.

```bash
python examples/run_uid_demo.py
python examples/run_association_demo.py
python examples/run_provenance_demo.py
```

## Expected Output

The example scripts are intentionally small and should produce readable outputs aligned with the methodological steps in the paper.

### `run_uid_demo.py`

This script prints example UIDs for an outcrop, a sample, and an analytical record, then parses them back into component fields.

Expected pattern:

```text
OUTCROP-REG_A-LOWER_MEMBER-OC001-SANDSTONE
SAMPLE-REG_A-LOWER_MEMBER-SP001-HANDSPECIMEN
RECORD-REG_A-LOWER_MEMBER-AR001-XRF
```

### `run_association_demo.py`

This script prints a ranked candidate list for one sample and shows why each candidate is retained, downgraded, or unresolved.

Expected pattern:

- one top-ranked outcrop with high-certainty and supporting evidence
- one weaker candidate retained by auxiliary evidence
- one unresolved candidate with insufficient combined evidence

### `run_provenance_demo.py`

This script prints:

- a forward query chain from one outcrop to its linked samples and analytical records
- a backward provenance restoration chain from one analytical record back to its parent sample and outcrop

## Method Summary

### 1. Cross-scale geological data organization

Three object levels are represented:

- outcrop
- sample
- analytical record

### 2. UID mechanism

The demo UID follows the paper-oriented pattern:

`<Level>-<Reg>-<Age>-<Seq>[-<Sub>]`

Field meanings:

- `Level`: object level such as `OUTCROP`, `SAMPLE`, or `RECORD`
- `Reg`: regional or source grouping tag used for cross-scale organization
- `Age`: stratigraphic age or related geological temporal grouping label used in the demo
- `Seq`: local sequence identifier
- `Sub`: optional subtype such as lithology class or analysis type

### 3. Rule-assisted association

Association is intentionally interpretable and organized into layers:

- high-certainty evidence
- auxiliary evidence
- candidate narrowing
- unresolved cases

The current demo rules operate over:

- identifier evidence
- source information
- stratigraphy
- lithology

The matcher returns both a score and human-readable evidence.
The demo is intentionally interpretable and does not rely on black-box model inference.

### 4. Bidirectional provenance

- Forward query starts from an outcrop and retrieves connected samples and analytical records.
- Backward provenance restoration starts from an analytical record and restores the parent sample and outcrop chain.

## Notes

- The demo data are anonymized and simplified.
- Coordinates, names, and identifiers are illustrative rather than production values.
- No database connection, API key, token, or private media asset is included.
