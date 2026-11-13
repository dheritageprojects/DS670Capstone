# U.S. Opioid Dispensing and Overdose Trends

Saint Peter's University graduate Data Science Capstone. Analysis period: 2020–2024.

## Current status

Initial dashboard-first implementation. No source data has been processed, validation targets have not been reproduced, and no dashboard has been deployed. Source URLs/files, column mappings, and authenticated Databricks access are still needed.

## First runnable increment

1. Place the two CDC CSV files in a Databricks Unity Catalog Volume.
2. Import `notebooks/01_pipeline.py` into Databricks Free Edition as a Python notebook.
3. Set the widgets to source paths, exact column names, and a writable schema. The overdose source must be restricted to one documented, all-drug, all-population county monthly series before running. Do not mix drug categories or demographic strata.
4. Run the notebook. Resolve duplicate keys or invalid values before continuing; do not silently drop them.
5. Use the resulting `county_year` table in a Databricks AI/BI dashboard following `dashboard/README.md`.

The initial annual measure uses December's reported 12-month-ending count. It is an overdose **count**, not a population-adjusted mortality rate. Dispensing rates retain the CDC source unit (verify prescriptions per 100 persons in the source metadata).

See [data quality](docs/data_quality.md), [methods](docs/methods.md), and [architecture](docs/architecture.md). The source schemas must be confirmed before treating this pipeline as validated.
