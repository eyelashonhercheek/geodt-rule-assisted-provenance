# Supplementary Table S4. Input versions, corrections and scoped interpretations

This supplement preserves historical scopes alongside the current D3 run. The source PDFs and registered D2 inputs remain unchanged. Counts describe workflow outputs unless a separate reference population is stated.

## S4.1. Historical and current full-corpus output scopes

| Input / policy | Rule links | Strong cands | Cand. sets | Open | Queries | Edges | Mean / all | Mean / kept |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Historical released workflow | 440 | 123 | 378 | 459 | 941 | 8,416 | 6.011 | 8.944 |
| Stage-A correction overlay on released workflow | 441 | 123 | 377 | 459 | 941 | 8,411 | 6.008 | 8.938 |
| Registered D2; fixed engine 0.4-r5 | 50 | 413 | 353 | 584 | 816 | 6,987 | 4.991 | 8.563 |
| Registered D3; same fixed engine 0.4-r5 | 52 | 396 | 374 | 578 | 822 | 7,031 | 5.022 | 8.554 |

In the table, Rule links, Strong cands, Cand. sets and Open denote the four final states; Queries counts nonempty queries. Mean / all divides edges by 1,400 and Mean / kept divides by nonempty queries. The historical means 6.01 and 8.94 round the released values. The D3 means before rounding are 7,031/1,400 = 5.022142857 and 7,031/822 = 8.553527981. State counts sum to 1,400 within each row. The released workflow and 0.4-r5 use different evidence and acceptance policies; their counts are therefore kept under their own versions.

The original 261 direct links can be traced to the recovered 16 April 2026 implementation and execution log. It matches format-normalized sample identifiers exactly, filters their candidates by available outcrop and section fields, and counts records retaining exactly one baseline row, without cross-report code translation. The logged count is 94 laser, 80 thin-section and 87 grain-size records; hyperspectral and XRF contribute zero under this rule. This direct branch belonged to the earlier 282/26/694/398 workflow, before the released 440/123/378/459 version. A replay from the retained source PDFs reproduces all three component counts and supplies 261 record–baseline pairs. It recovers the calculation rather than the original historical Excel binary; byte-level hashes of the original runtime inputs were not retained. The replay inputs, code and current hashes are supplied in support/historical_replay/.

The separate table-based total of 262 uses the directory source for THS014/TPA014, Chang82-14. The thin-section directory (PDF physical p. 3, entry 14) lists Yanhe No. 2, whereas the detail block (physical p. 21, printed p. 14) lists source 3. The recovered implementation prioritizes the detail source, leaving zero source-compatible candidates for baseline BS007 at Yanhe No. 2 and excluding this record from the direct count. This explains the count difference while preserving the source conflict. The historical ID-only count of 543 belongs to the later released workflow, which includes scoped identifier conversions and counts nonempty candidate sets before requiring unique source agreement. These historical definitions and the D3 acceptance policy are retained separately.

The recovered historical review files contain 30 inspection records and 20 unresolved-case suggestions, corresponding to the reported 15/15/20 groups. Pass entries in the 30-record table were assigned during workflow export; complete case-level human judgments for the 50-record aggregate were not retained. These files are archived for version tracing. The revised validation uses the new review of 89 distinct records: all 52 D3 accepted links, 30 stratified-random other-state records and seven diagnostic records, with source-page locators and returned human judgments in Tables S1–S2.

## S4.2. D2-to-D3 layer corrections and fixed-policy replay

| Baseline key | Sample label | Source | Original explicit layer | D3 explicit layer | Evidence scope |
|---|---|---|---|---|---|
| BS060 | 长7-11 | 延河8号 | 长6 | 长7 | Author project clarification and corresponding hyperspectral, XRF and laser fields |
| BS061 | 长7-12 | 延河8号 | 长6 | 长7 | Same scope, separately retained baseline row |

The physical-property baseline entries occur on PDF physical p. 5. Corresponding analytical blocks are HSR102/HSR103 (physical pp. 60–61), XRF0149/XRF0150 (physical p. 84), and LAS101/LAS102 (physical p. 64). These are physical-page locators; printed pages are retained separately in the registered documents. D3 changes the two explicit-layer fields and their normalized copies, retaining the original identifiers and baseline keys. The engine remains 0.4-r5.

Replay changes 29 full-workflow query outputs and 179 query/configuration outputs. Development target inclusion changes from 390/429 in D2 to 396/429 in D3. The six restored targets are the hyperspectral, XRF and laser counterparts of the two baseline rows. The earlier 39-target omission count splits into these six layer cases and 33 final documentary holds. The latter remain withheld in the D3 predictions.

The correction is an attributed input overlay. The project clarification is kept separate from literal report observations and from the reviewer judgments. The correction files are `inputs_D2.json`, `inputs_D3.json`, `all_changed_outputs_D3.csv` and `full_changed_outputs_D3.csv` in `reproducibility/`.

## S4.3. Project-specific code interpretations

| Code family | Retained interpretation | Evidence and application scope |
|---|---|---|
| Ordinary 长 identifiers | Identifier contains its Chang layer, e.g. 长82-1 → 长82 | Project numbering explanation; identifier-derived channel, dependent on the identifier |
| Numeric prefix + 长 identifier | Prefix can supply a numeric source interpretation; the remaining identifier supplies an alias | Report fields, numbering context and project interpretation; a numeric source alone is less specific than a complete outcrop name |
| Hyperspectral numeric-C identifier | Scoped C/长 correspondence, e.g. 1-C82-1 → 长82-1 | Report type and code context; explicit source/layer fields are retained separately |
| MNS | Manas/Manas River-related section | Project information; eight hyperspectral records; no additional unrecorded outcrop name supplied |
| SMH-J2t | Shuimohe code family | Project information; thirteen records |
| C-I, C-II, C-III | Panlongdong/Changxing Formation scheme; local layers 1, 2, 3 | Project explanation; five XRF records; roman numeral retained as a local layer indicator |
| J2T-7 / J2T-9 | Proposed relation to SMH-J2t-7/9 | Suffix, reported layer and lithology correspondence; retained as an interpretation |
| J3T-3 / J3Q-14 | Proposed Shuimohe batch interpretation | Less constrained project interpretation; no unique source field substituted |
| C81-D1-1 / D1-1 | Scoped hypothesis of shared numbering with omitted leading C component | Retained hypothesis; no undocumented outcrop inferred |
| XRF numerical-only 1,2,3,4,5,7,8,9,10,11,12 | Unknown origin | Available project information does not identify these eleven records; possible borrowing or instrument-control use is not established |

The table records interpretations and their boundaries; it does not add semantic aliases beyond those implemented in the registered 0.4-r5 projection. Parent, subsample, parallel-sample and repeated-measurement relations retain their own relation types. A shared label or interpreted code does not by itself assign a finer specimen-allocation relation.

## S4.4. Documentary conflicts and original values

Stage-A extraction changes, including the XRF0130 repeated concatenated identifier and the XRF row-173 report-page correction, remain attributed to their original overlay. A page-number correction is not a relationship confirmation. The withdrawal of TPA014's earlier cross-source consistent label remains recorded as a conflict rather than a confirmed source identity.

Grain-size disagreements are retained individually. EX033 supports the detail-page 长81-51 target BS045 (physical p. 63, printed p. 57) while preserving directory 长81-52. EX056 supports detail-page 长81-44 target BS039 (physical p. 57, printed p. 51) while preserving directory 长81-45 and the author's transcription-error explanation. Frozen predictions continue to apply their documentary holds, so both are counted as positive-target retrieval omissions. EX005's editorial reason correction points to grain-size physical p. 106 / printed p. 100, 长62-8 at 延河9号, BS076; its supported judgment is unchanged.

The source hashes, registered inputs, predictions, review ledger and later editorial annotations provide separate provenance for the calculations. The paired analysis and explanatory diagrams retain the registered input tables, engine and human judgments.
