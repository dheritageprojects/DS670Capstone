# Data-quality plan

These previous pandas values are comparison targets, never generated results:

| Metric | Target |
|---|---:|
| Raw dispensing records | 18,864 |
| Raw overdose records | 226,368 |
| Matching county FIPS | 3,142 |
| Merged county-years | 15,710 |
| Complete observations | 8,180 |
| Counties in complete cases | 2,385 |
| Missing dispensing rates | 297 |
| Missing/suppressed overdose counts | 7,298 |

The notebook reports actual values and differences. Differences must be investigated against release versions, series selection, join semantics, and annualization; do not alter data to force a match. Raw row counts describe files before year filtering.

Blocking checks cover valid five-digit FIPS, non-null integer year/month keys, months 1–12, nonnegative numeric parsing, and unique dispensing county-year and overdose county-year-month keys. Valid source years outside 2020–2024 are filtered out rather than rejected. Unknown nonnumeric values fail parsing; approved suppression/missing tokens remain null. Duplicate keys fail before joins.

The panel is the union of observed dispensing and December overdose county-year keys. It does not invent counties or years absent from both sources. Compare its coverage with the prior pandas merge before expecting 15,710 rows. Flags distinguish missing measures but do not distinguish an absent source row from suppression. Raw strings remain in intermediate DataFrames during processing and in the archived CSV snapshots; the final county-year tables do not retain the source footnotes or raw numeric strings.

Primary processing has executed successfully against real sources in GitHub Actions and Databricks. Source suppression markers and alias duplicates have been inspected, and the user confirmed the original dashboard and filters work. See `source_inspection.md` for current results; `pandas_reconciliation.md` explains the target differences as a reproduced historical comma-parsing defect. Sensitivity implementation and independent reference checks are in `02_sensitivity.py` and `tests/check_sensitivity.py`; its five-table Delta persistence is now verified in Databricks (see `sensitivity_verification.md`); the live annual comparison SQL has run there and the user reviewed the sensitivity dashboard page. CDC source landing pages and definitions are verified; exact export/download and snapshot release provenance still need completion.

## Historical benchmark interpretation

The uploaded pandas export reproduces every historical target. Its direct `pd.to_numeric(errors="coerce")` lost 23 comma-formatted reported overdose counts. Comma normalization restores the current 8,203 complete rows, 2,388 complete counties, and 7,275 missing overdose values. Keep the old target values as historical evidence; the three nonzero differences are explained corrections, not unresolved failures or CDC suppression. Regression tests ensure numeric formatting is not confused with missingness. See `pandas_reconciliation.md` and the row-level CSV.
