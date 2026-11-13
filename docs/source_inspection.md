# Uploaded source inspection

## Dispensing: opioid_dispensing_2026_update.csv

SHA-256: `8cd88e062cab18e28d7ec7baa85f77c392c4e29665fb2cc35878c80023608f4d`

Computed using Python's CSV reader on the supplied file:

| Check | Observed |
|---|---:|
| Raw records, 2019–2024 | 18,864 |
| Distinct county FIPS | 3,144 |
| Records, 2020–2024 | 15,720 |
| Unavailable rates, 2020–2024 | 307 |
| Duplicate county-year keys, 2020–2024 | 0 |
| Invalid five-digit FIPS, 2020–2024 | 0 |

Mappings: `Location` → county FIPS, `Year` → year, `STATE_NAME` → state, `COUNTY_NAME` → county label, `Opioid Dispensing Rate` → numeric rate. The similarly named `Opioid Dispensing Rate (per 100 persons)` column contains display bins such as `< 17.7`, not individual numeric rates. Preserve `Data unavailable` as null.

The raw row count matches the prior target. The standalone analysis-period data have 10 more records and 10 more missing rates than the prior merged-data targets; this does not establish why the difference occurs. Check the overdose county universe and prior join rules before changing join semantics. Do not remove counties merely to reproduce a target.

## Overdose: overdose_deaths_2026_update.csv

Inspected the supplied ZIP containing one 43,712,981-byte CSV. Raw records: 226,368; years 2020–2025; 3,142 unique FIPS. `Data as of` is `07/05/2026` in every record (preserved as source text). `FIPS` needs zero-padding; `Year` and `Month` are numeric strings. The measure is `Provisional Drug Overdose Deaths`. Blank values carry an explicit suppression footnote; literal zero is a reported zero and remains zero.

There are 144 duplicate county-month key groups across the full file: FIPS 51005 (Alleghany / Clifton Forge city) and 51019 (Bedford / Bedford city), each over 72 months. All source columns except COUNTYNAME agree within each group. Collapse these identical analytic observations; never sum them. Chugach (02063) and Copper River (02066) appear only in dispensing. No geographic crosswalk or reassignment is attempted.

December snapshots, restricted to 2020–2024, inner-joined on common county-year keys yield:

| Metric | Actual | Prior target |
|---|---:|---:|
| Matching counties | 3,142 | 3,142 |
| Merged county-years | 15,710 | 15,710 |
| Complete observations | 8,203 | 8,180 |
| Complete-case counties | 2,388 | 2,385 |
| Missing dispensing | 297 | 297 |
| Missing overdose | 7,275 | 7,298 |

The 23-observation discrepancy has been resolved as a historical pandas comma-parsing failure; see `pandas_reconciliation.md`. Legacy parsing reproduces all previous targets; comma normalization reproduces current pipeline results. Primary PySpark execution has passed locally, in CI, and in Databricks.

The pipeline retains a full coverage panel for the dashboard and a separate common-key table for target comparison. Quarterly and rolling-average comparisons are implemented and locally tested; their live annual comparison SQL has run in Databricks. See `sensitivity.md` for coverage findings and separate persistence/UI deployment status.

Compressed public CDC source snapshots are versioned under `sources/` for reproducible CI runs. CDC source landing pages and definitions are documented in `source_citations.md`; exact original export/download dates and file release identity remain unresolved.
