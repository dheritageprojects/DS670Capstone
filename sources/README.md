# Versioned source snapshots

These compressed CSV snapshots are the public CDC files supplied for this project. They contain county-level aggregate data and no credentials. The ZIPs allow GitHub Actions to run against the same input release without relying on mutable external downloads. See `docs/source_inspection.md` for schema and release observations. Original CDC download URLs remain to be supplied.

Run `python tests/run_pipeline.py` with Python 3.12, Java 21, and `pyspark==4.0.1`. It executes source checks and the actual notebook with local Spark, using temporary Parquet tables. Databricks continues to default to Delta tables. This check does not exercise Unity Catalog permissions, Databricks compute, Delta-specific behavior, or AI/BI dashboard deployment.
