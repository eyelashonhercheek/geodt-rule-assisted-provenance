# Historical direct-link replay and review-file provenance

This bundle preserves the recovered 16 April 2026 direct-link implementation and a new replay of its 261-record result. These are computational source/sample-label links. The original historical Excel output binary and runtime input hashes were not recovered. The retained PDFs and input workbooks are versioned and hashed here.

The direct rule uses exact format-normalized sample identifiers, then available source fields, and requires one remaining baseline row. It does not apply cross-report identifier aliases. Its logged and replayed components are 94 laser, 80 thin-section and 87 grain-size records. The hyperspectral and XRF normalized identifiers have zero direct overlap without scoped conversions. The 800-row trace covers the three direct-overlap report types. The 261 accepted replay rows all use detail-page sources, without the directory fallback.

Run from the unpacked supplementary archive root with Python 3.10 or later:

```
python -m pip install -r support/historical_replay/requirements.txt
python -B support/historical_replay/replay_direct_links.py --out-dir historical_replay_output
```

The command reads `原始报告/` and `support/historical_replay/input_tables/`; it writes to a new output folder. `--pdf-root`, `--table-root` and `--out-dir` can select other working-copy locations. Pinned package versions describe this replay environment, not an asserted historical environment.

Expected counts: 400 laser, 200 thin-section and 200 grain-size records parsed; 261 direct links with the components above. `function_sources/` preserves original code-message text. The replay executes only reviewed function definitions from those files, not their original top-level processing or export commands.

The historical review resource has 30 inspection records and 20 unresolved-case suggestions. The original workflow export assigned the 30-record table's pass entries from system states. A 50-row trace recovers their identifiers and record origins; it is not a completed independent 50-case validation. The revised performance evaluation uses the separately supplied 89-record human review.

THS014/TPA014 explains the 261/262 difference: the directory at thin-section PDF physical page 3 lists Yanhe No. 2, whereas the detail at physical page 21, printed report page 14, lists source 3. The recovered direct rule uses the detail source and excludes BS007 at Yanhe No. 2. The discrepancy remains recorded, without declaring which source is physically correct.
