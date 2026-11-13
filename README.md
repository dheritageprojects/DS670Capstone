# U.S. Opioid Dispensing and Overdose Trends

Saint Peter's University graduate Data Science Capstone. Analysis period: 2020–2024. Workflow: **GitHub → Codex → Databricks → Dashboard**.

The primary PySpark pipeline has run in Databricks, both dashboard pages have user-reported review, and research SQL results have been independently reproduced from frozen source snapshots. All historical targets have been reproduced; the three current differences are explained by the old pandas conversion discarding comma-formatted reported counts. The current pipeline already uses corrected parsing; see [reconciliation evidence](docs/pandas_reconciliation.md). The separate sensitivity notebook's five Delta tables still need Databricks execution evidence. The live sensitivity dashboard and research queries already work without those tables.

## Start here

- [Reproduction and handoff guide](docs/reproducibility.md): clean-checkout checks, Databricks execution order, access, pins, and known gaps.
- [Requirements audit](docs/requirements_audit.md): requirement-by-requirement evidence and remaining submission work.
- [Capstone report draft](docs/capstone_report.md): methods, verified findings, limitations, and incomplete data references.
- [Research findings](docs/research_findings.md): focused numerical results and query evidence.
- [Architecture](docs/architecture.md), [quality](docs/data_quality.md), [source inspection](docs/source_inspection.md), and [sensitivity methods](docs/sensitivity.md).

## Reproduce the checks

With Python 3.12 and Java 21, from the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-ci.txt
.venv/bin/python sources/verify_manifest.py
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python tests/run_pipeline.py
```

GitHub Actions runs these checks plus syntax checks. Local Spark uses temporary Parquet tables; Databricks notebooks default to Delta. Source ZIPs and their compressed/uncompressed checksums are recorded in [the manifest](sources/manifest.json). [Verified CDC citations and definitions](docs/source_citations.md) document source-estimated dispensing rates and the prescriber-versus-resident geography mismatch. CDC source landing pages are verified; exact export/download and snapshot release history remain incomplete.

## Databricks and dashboard

Import `notebooks/00_databricks_setup.py` and Run all for primary setup. It downloads checksum-verified artifacts from a pinned historical commit, creates the source Volume, and runs the primary pipeline. Separately import/run the current `notebooks/02_sensitivity.py` for the five sensitivity output tables. See the runbook before rerunning: project source files and output tables are overwritten, and a failed multi-table run can leave mixed-generation outputs.

[Open the existing dashboard draft](https://dbc-dc957048-d7f2.cloud.databricks.com/sql/dashboardsv3/01f1df0509d010f987459df183dcdd91?o=7474646615740609). Its original page uses the full coverage panel; the sensitivity page uses read-only Volume SQL and the common-key panel. The saved multi-page definition is `dashboard/opioid_trends.lvdash.json`. Publication/audience status must be checked separately from functional review.

Reported overdose counts are not mortality rates. Suppression remains missing; overlapping monthly windows are never summed into annual deaths. Smoothed values are derived snapshot means, not imputed annual counts. County dispensing means are unweighted, not national/state dispensing rates. All associations are descriptive and do not establish causation.
