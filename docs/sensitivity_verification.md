# Databricks sensitivity persistence verification

Status: **verified** after the user ran `notebooks/02_sensitivity.py`. This closes the previously documented five-table Delta execution gap. Verification was read-only; no data, queries, or dashboard definitions were changed during this step.

## Stored tables

`workspace.information_schema.tables` reports `DELTA` for all five tables. Readback produced:

| Table in workspace.capstone | Rows |
|---|---:|
| overdose_quarterly | 62,840 |
| overdose_rolling3 | 188,520 |
| sensitivity_county_year | 62,840 |
| sensitivity_summary | 60 |
| sensitivity_paired | 20 |

Expected row counts are independently derived from the frozen source keys/methods, not inserted into tables. The monthly series contains 3,142 county FIPS × 60 analysis months after identical aliases collapse; quarterly snapshots retain four months per year. The annual sensitivity table contains four methods for every common-key county-year.

## Checks and numerical agreement

All checks found zero violations/mismatches:

- Annual county-year-method keys and measures match the independently validated live annual SQL dataset, including nulls and complete-case flags, at absolute tolerance 1e-9.
- No duplicate keys in any of the five saved outputs.
- No annual strict mean is populated with incomplete required periods; all imputation flags remain false.
- Quarter-end months and quarter numbers are valid, and every saved quarterly count matches the source.
- Every saved rolling row matches the source count, calendar-window row count, observed-month count, and independently recomputed strict three-month mean. Checks include cross-year windows and the unavailable initial windows in January/February 2020.
- All 60 summary rows and all 20 paired-comparison rows match standard-library reference calculations from the frozen CSV snapshots, including eligibility/observed/complete counts, overall/complete means, Pearson correlations, and paired mean/absolute differences (relative and absolute tolerance 1e-9).

The fixed comparison cohort remains 865 counties across 2020–2024. These checks validate saved outputs for the supplied release; they do not recover original export dates, supply managed runtime/job metadata, or imply a dashboard publication action.

## Reproducible evidence

- `analysis/verify_sensitivity_persistence.sql`: table counts, primary annual comparison, keys, strict-window, quarter, and imputation checks.
- `analysis/verify_snapshot_windows.sql`: full quarterly/source and rolling/calendar-window comparisons.
- `analysis/sensitivity_{checks,formats,summary,paired,windows}_verification.json`: complete provider query exports with identifiers and truncation status; no selected-row summaries substituted.
- `analysis/verify_sensitivity_exports.py`: independently checks saved summary/paired results and requires all storage/SQL checks to pass.
- `tests/test_persistence_exports.py`: reruns that reference check in CI. CI verifies recorded Databricks evidence against frozen inputs; it does not reconnect to Databricks on every push.

Run the independent check from the repository root:

```bash
python -m analysis.verify_sensitivity_exports
```

To refresh evidence after changing inputs, rerun both read-only SQL files and export the complete new table summaries/paired results and format metadata. Preserve the old evidence if comparing releases. Rerunning the local checker alone does not refresh or prove the current live workspace state.

[Explore in Databricks](https://dbc-dc957048-d7f2.cloud.databricks.com/one/chat/threads/7523063dc5f746e29f110cef31fc884a?o=7474646615740609&utm_source=genie_chat_mcp)

[Explore in Databricks](https://dbc-dc957048-d7f2.cloud.databricks.com/one/chat/threads/5fca41fa5ed844e6b4e5b52c133fa688?o=7474646615740609&utm_source=genie_chat_mcp)
