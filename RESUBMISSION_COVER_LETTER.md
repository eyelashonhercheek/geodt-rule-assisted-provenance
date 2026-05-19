Dear Prof. Gómez-Hernández,

Thank you for evaluating our previous submission, CAGEO-D-26-00780, entitled
"An Auditable Cross-Scale Provenance Recovery Framework for Fragmented
Geological Records." The previous decision noted that the lack of
reproducibility of the reported results made the proposed framework difficult to
evaluate.

We have addressed this concern directly. In the revised submission, we now
provide a public reproducibility package containing the full released tabular
dataset, normalization rules, field inventory, regenerated linkage outputs, and
validation code. The package is archived with a DOI:

https://doi.org/10.5281/zenodo.20279191

The corresponding GitHub repository is:

https://github.com/eyelashonhercheek/geodt-rule-assisted-provenance

The release includes two levels of reproducibility. First, a minimal demo
dataset allows readers to inspect the evidence operators, conservative fallback,
status assignment, and provenance tracing logic record by record. Second, the
full-release workflow regenerates the 1400-row linkage table from the released
baseline and analytical-record workbooks and verifies that the regenerated rows
and summary statistics match the reported manuscript results. The validation
commands are:

```bash
python examples/generate_full_linkage.py
python examples/validate_full_release.py
python examples/validate_expected_results.py
```

The expected full-release validation output is:

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

We also revised the manuscript's Code and Data Availability statement and
removed the previous limitation that the complete dataset could not be publicly
released. The revised manuscript now states that the released tabular data and
code reproduce the reported workflow outputs and that the data are intended for
public archival release under a CC BY 4.0-compatible data license.

We hope that these changes resolve the reproducibility concern and allow the
manuscript to be evaluated on its scientific and methodological merits.

Sincerely,

Yanlin Shao  
on behalf of all authors
