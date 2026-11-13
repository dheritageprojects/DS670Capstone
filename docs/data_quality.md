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

Blocking checks: valid five-digit FIPS, non-null years/months, allowed analysis years/months, nonnegative numeric values, and unique dispensing county-year and overdose county-year-month keys. Unknown nonnumeric values fail parsing; approved suppression/missing tokens remain null. Duplicate keys fail before joins.

The panel is the union of observed dispensing and December overdose county-year keys. It does not invent counties or years absent from both sources. Compare its coverage with the prior pandas merge before expecting 15,710 rows. Flags distinguish missing measures but do not distinguish an absent source row from suppression; source raw strings are retained in normalized views for investigation.

Primary processing has executed successfully against real sources in GitHub Actions and Databricks. Source suppression markers and alias duplicates have been inspected, and the user confirmed the original dashboard and filters work. See `source_inspection.md` for current results and unresolved target differences. Sensitivity implementation and independent reference checks are in `02_sensitivity.py` and `tests/check_sensitivity.py`; its Databricks deployment remains pending. Original CDC URLs and full release provenance still need completion.
