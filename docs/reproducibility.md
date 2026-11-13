# Reproduction and handoff guide

## What this reproduces

The supplied CDC snapshots, primary 2020–2024 county-year pipeline, strict annualization comparisons, descriptive research outputs, and a two-page Databricks dashboard. Source identity is recorded in `sources/manifest.json`; the original CDC URLs and release documentation remain incomplete. GitHub Actions success demonstrates local Spark execution and reference agreement, not Databricks permissions or browser rendering.

## Software and access

- Git and a checkout of this repository; record `git rev-parse HEAD` for each run.
- Local/CI: Python 3.12, Java 21, PySpark 4.0.1. `requirements-ci.txt` pins the direct Spark dependency; it is not a complete environment lockfile. GitHub uses `ubuntu-latest`, so its OS image can change.
- Databricks: Free Edition Python serverless compute, permission to use the `workspace` catalog, create/use `workspace.capstone`, create/write its `source_files` Volume, and create/overwrite project tables. The exact managed Databricks runtime version was not captured; do not equate the CI Spark version with it.
- Notebook setup downloads only from `raw.githubusercontent.com`, using HTTPS and fixed SHA-256 checks. If the workspace blocks outbound downloads, upload the verified CSVs to the same Volume and run `01_pipeline.py` with explicit paths instead.
- Dashboard: SQL warehouse access plus read permission on primary tables and, for sensitivity, the source Volume. Genie authentication does not grant this assistant notebook execution tools. Do not store credentials in Git.

## Local verification from a clean checkout

Run from the repository root, with Java 21 available:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-ci.txt
.venv/bin/python sources/verify_manifest.py
.venv/bin/python -m compileall -q notebooks tests dashboard analysis sources
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python tests/run_pipeline.py
```

The full runner extracts the ZIPs to temporary storage, executes the actual primary and sensitivity notebooks on local Spark, writes/reads temporary Parquet tables, checks every strict annual measure against independent CSV arithmetic, and checks the annual dashboard SQL against the same reference. The original source files are not altered. Managed Databricks-only operations in `00_databricks_setup.py` are syntax-checked, not executed locally. The research tests reproduce all 60 association/trend rows and 255 state-year rows from frozen source files, including average-rank handling of ties.

GitHub Actions runs the same checks on push, pull request, or manual workflow dispatch. A failed check must be investigated, not repaired by editing source data or target counts. Historical target differences are printed and documented rather than treated as exact acceptance thresholds.

## Databricks execution order

1. **Primary setup:** import `notebooks/00_databricks_setup.py` as Python, attach serverless compute, then Run all. It creates `workspace.capstone` and the managed `source_files` Volume, fetches the exact snapshot and primary pipeline artifacts pinned to commit `e6f95284cf1b435302de029b9a47c6cf46872bff`, verifies their hashes, and executes the primary pipeline. This historical pin is intentional; later checkout changes do not silently change it.
2. **Primary inspection:** inspect `workspace.capstone.quality_report`, row/key counts, and source coverage. The full panel `county_year` contains 15,720 rows for these files; `county_year_common` has 15,710 rows. Only the latter is compared with historical merged-data targets. The two dispensing-only FIPS are 02063 and 02066. Compare outputs with `docs/source_inspection.md`.
3. **Sensitivity persistence:** separately import the current `notebooks/02_sensitivity.py` from a recorded repository revision and Run all. Defaults read the existing source Volume and common-key table, leaving primary tables unchanged. Confirm five output tables: `overdose_quarterly`, `overdose_rolling3`, `sensitivity_county_year`, `sensitivity_summary`, `sensitivity_paired`. This Databricks Delta execution remains pending evidence, even though local Spark tests and the live dashboard comparison SQL passed.
4. **Research:** run `analysis/associations_trends.sql` and `analysis/geographic.sql` as read-only SQL in the workspace. These use existing primary tables and the source Volume; they do not require the five persisted sensitivity tables. Preserve the complete SQL results with query identifiers, schema, and truncation status. Never substitute Genie's selected-row narrative for a full export.
5. **Dashboard:** use the existing dashboard ID in `dashboard/deployment.json`; avoid creating duplicate dashboards. The saved `dashboard/opioid_trends.lvdash.json` includes both pages. The original page reads the full coverage panel and quality report; the sensitivity page reads the source Volume and common-key panel through `dashboard/sensitivity_dataset.sql`. Verify warehouse and permissions before running it. Existing dashboard pages were reviewed by the user; recheck after source/schema/code changes.

Setup and processing overwrite their own output tables and source files when rerun. These operations are not transactional across all tables. If any stage fails, diagnose it and rerun the complete affected stage before using mixed-generation outputs. Stop downstream refreshes until a consistent run is available. There is no scheduled production job or automated end-to-end Databricks deployment.

## Refreshing results and documentation

`python analysis/build_report.py` rebuilds `docs/research_findings.md` and the CSV exports from the saved Databricks JSON results; it does not execute SQL or download new data. Preserve this evidence when reproducing the current analysis. After a deliberate new source release, update the manifest, source inspection, notebook artifact pins where appropriate, full result exports, reference checks, and report together. Explain differences; do not silently overwrite the historical benchmark.

The initial `dashboard/build_dashboard.py` builds only the original baseline page and would omit later sensitivity additions if used as a replacement. To reproduce the current dashboard, use the saved multi-page JSON. `build_sensitivity.py` appends to a freshly exported baseline and refuses an already-present sensitivity page; inspect existing assets rather than blindly rerunning creation.

## Evidence and remaining handoff inputs

- Primary Databricks tables and quality results: verified through read-only queries.
- Live sensitivity coverage query: verified in Databricks; source observations exported in `docs/sensitivity_coverage.csv`.
- Original dashboard/filter behavior: explicit user confirmation. Sensitivity page: user reported review, with no failure reported; no independent browser test or screenshot is claimed.
- Research: full provider-result exports plus independent source calculations and automated tests.
- Still required: original CDC URLs/release metadata; previous pandas code or release for the 23-observation discrepancy; executed sensitivity Delta-table evidence; final report author/course/advisor details and rubric; publication/audience decision.
