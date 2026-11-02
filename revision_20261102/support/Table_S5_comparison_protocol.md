# Supplementary Table S5. Baseline and ablation execution protocol

## S5.1. Common inputs and four retrieval baselines

All twelve methods use the same registered D3 population: 1,400 analytical queries and 100 separately keyed baseline rows. Analytical measurement values and reference targets are not matching features. Baselines are defined in `reproducibility/run_author_revision_v5.py:basic`; feature projection and the eight workflow configurations are defined in `r5_engine.py`.

| Baseline | Candidate entry | Source, layer and lithology handling | Endpoint |
|---|---|---|---|
| Stored-identifier literal equality (`raw_id`, retained software key) | Nonempty equality of the stored `sample_id_raw` strings | No contextual filters; inherited extraction-table formatting retained | All literal stored-string hits |
| Format-normalized identifier (`format_id`) | Nonempty normalized-string equality | None | All normalized-ID hits |
| Parsed-alias identifier (`parsed_alias_id`) | Nonempty intersection of scoped alias sets | Fields can contribute to registered alias construction; no subsequent contextual filters | All alias hits |
| Strict multi-field (`strict_multifield`) | Same alias hits; if query ID is missing, start from all baseline rows | If named source exists, require exact named-source equality; otherwise, require numeric-source equality when available. If query explicit/coded layer exists, require literal overlap with a baseline explicit/coded layer. If query lithology exists, require lexical lithology support. Missing query constraints are skipped. There is no context entry for a present but unmatched ID, fallback, or final documentary hold. | All candidates surviving this conjunction |

The retained software key `raw_id` names a stored-string baseline. It does not recreate original-PDF typography. Some legacy analytical strings were already compacted during extraction: LAS002 stores 长82-1, whereas its retained detail transcription and baseline string contain 长 82-1. The 2/429 result reflects this formatting history; the format-normalized, alias and strict baselines provide the subsequent comparisons.

For strict matching, a populated query field with no compatible baseline value fails the corresponding constraint. An absent query field imposes no constraint. A query with an existing but unmatched ID remains empty; a query without an ID can be filtered from the full baseline. The strict baseline intentionally tests a conventional conjunctive policy, while the full method tests scoped compatibility, contextual entry, fallback and holds. The strict endpoint is not given the full workflow's native acceptance labels. Candidate retention and candidate edges can be compared directly; accepted-link precision evaluates the full policy that actually issues accepts.

Alias construction retains the normalized ID, optionally strips a numeric prefix before an ordinary Chang ID, and applies the numeric-C/Chang rule only to the hyperspectral family. A numerical-only ID can be combined with an explicit Chang layer when the identifier, alias and stratigraphy channels are enabled. Arbitrary suffix deletion is not implemented. Identifier-derived layer support retains its dependency on that identifier.

## S5.2. Full workflow and seven ablations

`1` enables the corresponding `Config` flag; `0` disables it. Each row is evaluated under the same registered input and reference scopes.

| Configuration | Identifier | Alias | Source | Stratigraphy | Lithology | Fallback | Conflict gate |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| no_identifier_evidence | 0 | 1 | 1 | 1 | 1 | 1 | 1 |
| no_alias | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| no_source | 1 | 1 | 0 | 1 | 1 | 1 | 1 |
| no_stratigraphy | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| no_lithology | 1 | 1 | 1 | 1 | 0 | 1 | 1 |
| no_fallback | 1 | 1 | 1 | 1 | 1 | 0 | 1 |
| no_conflict_gate | 1 | 1 | 1 | 1 | 1 | 1 | 0 |

Feature removal propagates to dependent channels. Removing identifier evidence removes raw/normalized IDs, aliases, identifier-derived layers and prefix-derived sources, while retaining explicit report sources and layers. Removing stratigraphy removes explicit/coded layer channels and layer-assisted numerical-ID reconstruction but preserves whole-ID comparison. Removing aliases disables prefix stripping and C/Chang recoding; ordinary Chang-derived layers remain if enabled by the other flags. Removing source context removes source fields, source-based entry/filtering and dependent source flags. The unchanged native acceptance condition still requires complete named-source agreement; hence this configuration issues no native accepts. Removing lithology disables only that lexical operator.

The conflict-gate switch is composite: it controls explicit named-source exclusions, explicitly comparable layer exclusions and final holds arising from document flags. Its result is therefore a joint policy-sensitivity comparison, not an isolated final-hold ablation. Native acceptance still requires the same high-evidence conditions and absence of flags even when the gate switch is off. In particular, the 215 target-matching native accepts without stratigraphy describe that configuration's policy outputs; they do not establish higher independently measured precision.

## S5.3. Operators and missing or conflicting fields

Candidate entry first uses alias-ID hits. Without ID hits, it uses available source and layer candidates, preferring their nonempty intersection. If both source and layer sets exist but their intersection is empty, enabled fallback retains the source set. Source-only and layer-only entry handle available context. This contextual entry differs from the strict baseline's treatment of a present but unmatched ID.

Named sources use the explicit comparison in `common.source_compat`. Only explicitly different comparable names are hard exclusions when the gate is enabled. Unresolved naming scope within a record is logged during projection; cross-record names outside that explicit-difference relation survive the hard exclusion. A numeric-source label prefers matching numeric-source candidates when they exist; otherwise candidates remain with an uncertainty flag. Original numeric labels and complete source names remain separately represented.

Hard stratigraphic exclusions compare explicit report fields through `common.layer_compat`. Within the implemented system, incompatible single-digit Chang units are explicitly comparable; finer/coarser Chang labels and unresolved different systems remain for review. `layer_support` logs literal overlap of explicit/coded channels, with their dependency recorded. It is not a separate independent vote or an additional hard filter in the full method. The strict baseline instead requires this overlap when its query layer channel is populated.

Lexical lithology support uses literal equality or shared terms from the fixed list 粉砂岩、砂岩、泥岩、灰岩、砾岩. If a nonempty supported subset exists, it is retained. If no candidate has lexical support, fallback retains the pre-lithology candidates when enabled; otherwise the set is emptied. The method therefore makes this weak evidence recoverable.

Document flags are projected from source/identifier disagreements, prefix/source inconsistency and directly conflicting coded/explicit numbering; unresolved granularity is recorded separately. A final documentary hold archives the candidates and emits an unresolved output. Remaining outputs follow main-text Table 2. Native acceptance requires one final candidate, format-only ID equality, complete named-source equality, one candidate before weak lithology, a non-inferred locator, no unresolved review reasons and no projected flags.

## S5.4. Reference scopes and paired comparisons

The 429 development queries have one documentary target each. Evidence strata retain construction dependencies (250 directory, 93 hyperspectral, 85 XRF, one same-report). The 71 supported human-review queries form a separate positive scope drawn from the 89 reviewed records. Their selection arms are retained in Tables S1–S2. Overlapping record keys identify shared observations; the scopes are not added as independent populations. The eighteen insufficient-evidence judgments remain unknown.

Target inclusion is counted at each method's final candidate endpoint. Candidate edges sum the final set sizes for those same queries. Baselines have no native acceptance rule, so their automatic-accept values are left blank. Full-policy precision uses the complete 52-accept population. The pooled reviewed-positive inclusion describes the selected 71 records; neither general-population recall nor correct-rejection performance is inferred from that partial positive scope.

`analyze_R25_pairs.py` independently replays all 1,400 full and strict outputs and asserts their agreement with the frozen predictions before pairing target retention. Documentary outcomes are 383 both, 13 full-only, 33 strict-only and zero neither. Reviewed-positive outcomes are 68 both, one full-only, two strict-only and zero neither. It saves `paired_retention_R25.json` and the per-case `paired_case_ledger_R25.json`, including operator traces. The eleven documentary fallback gains and two unresolved-layer gains are distinct from EX076's reviewed contextual-entry case.

## S5.5. Computational diagnostics and interpretation updates

`run_D3_diagnostics.py` compares exact named-source blocking against the full candidate pool, counting candidate-pool checks and output changes. The observed counts are 140,000 versus 102,095 checks, with 37 changed outputs. All 37 queries have named sources after projection. Blocking removes their global ID hits and switches entry to source-and-layer (35) or source only (two); all change from empty/unresolved to nonempty candidate sets, with zero native accepts. Counts by family are fourteen laser, eleven thin-section and twelve grain-size. These entry changes are separate from interpretation of the named-source field. They measure this comparison workload, rather than elapsed runtime or indexing complexity. Its six source/layer/lithology permutations keep candidate entry and final holds fixed. Identical candidate sets in those permutations characterize that setup.

The technical record key is derived from the source file/row registration. `common.append_semantic_version` and `test_r5.py` illustrate appending changed interpretations under a stable entity key; the manuscript does not depend on an externally deployed UID registry. D2/D3 inputs demonstrate the layer correction under the same baseline keys.

## S5.6. Execution

From the unpacked supplementary archive, use a Python 3 environment with its standard library:

```
python -B support/reproducibility/reproduce_review89.py
python -B support/reproducibility/analyze_R25_pairs.py
```

The first command recomputes 48 configuration-by-review-scope rows from Tables S1–S2 and the frozen predictions. The second replays full/strict queries and verifies the paired results. To replay all twelve D2/D3 configurations, run the following on a working copy of the package, because it writes regenerated comparison files alongside the inputs:

```
python -B support/reproducibility/run_author_revision_v5.py
```

SHA-256 hashes for the supplied files are listed in the archive-root `SHA256_manifest.csv`. Historical suffixes in script and output filenames identify the retained computational versions. The paired analysis preserves the recovery engine and the returned human judgments.

## S5.7. Source locators and metric definitions

The Figure 3 cases are singleton strong candidates in the fixed outputs, with source associations supported by R1. Physical PDF pages are direct locators. For its hyperspectral/XRF cases, the report-page numbers are directory references; the inspected detail pages do not show printed page labels. Table S1 retains the registered `detail_printed_page` column name. For hyperspectral and XRF records this field carries the directory-referenced report-page value; the physical page is the direct locator, and a printed page label may be absent from the detail page. The XRF detail has no separately supplied source field; its numeric prefix contributes the scoped source interpretation.

Retrieval coverage is 822/1,400 = 58.71%; native-acceptance coverage is 52/1,400 = 3.71%. These complements to accepted-link precision use the full query population and do not change any predictions or judgments.
