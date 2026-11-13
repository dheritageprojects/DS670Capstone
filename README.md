# U.S. Opioid Dispensing and Overdose Trends

Saint Peter's University graduate Data Science Capstone. Analysis period: 2020–2024.

## Current status

Dashboard-first implementation with supplied CDC snapshots and automated local Spark/GitHub Actions checks. Source inspection reproduces five of eight prior targets; complete-case and mortality-missingness differences remain documented in `docs/source_inspection.md`. Primary tables are deployed in Databricks and the user confirmed the original dashboard and filters work. Sensitivity comparisons are implemented separately; see `docs/sensitivity.md`. Original CDC URLs are still needed.

## First runnable increment

1. Place the two CDC CSV files in a Databricks Unity Catalog Volume.
2. Import `notebooks/01_pipeline.py` into Databricks Free Edition as a Python notebook.
3. Set the widgets to source paths, exact column names, and a writable schema. The overdose source must be restricted to one documented, all-drug, all-population county monthly series before running. Do not mix drug categories or demographic strata.
4. Run the notebook. Resolve duplicate keys or invalid values before continuing; do not silently drop them.
5. Use the resulting `county_year` table in a Databricks AI/BI dashboard following `dashboard/README.md`.

The initial annual measure uses December's reported 12-month-ending count. It is an overdose **count**, not a population-adjusted mortality rate. Dispensing rates retain the CDC source unit (verify prescriptions per 100 persons in the source metadata).

See [data quality](docs/data_quality.md), [methods](docs/methods.md), and [architecture](docs/architecture.md). The source schemas must be confirmed before treating this pipeline as validated.

## Automated execution

GitHub Actions runs `.github/workflows/validate.yml` on pushes and pull requests. It executes both Python source checks and the full Spark notebook against versioned source snapshots, persisting temporary Parquet tables. See `sources/README.md` for local setup and limits. Databricks runs retain Delta as the default output format.
