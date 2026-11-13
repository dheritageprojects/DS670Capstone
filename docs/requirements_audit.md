# Requirements audit

Review date: November 13, 2026. Status is based on repository artifacts, recorded Databricks query results, CI runs, and the user's dashboard review. This is an evidence audit, not a declaration that the capstone is ready for submission.

Legend: **Done** = implemented with stated evidence; **Partial** = implemented but limited or awaiting an execution step; **Open** = required evidence or action absent.

## Original technical requirements

| Requirement | Status | Evidence and remaining work |
|---|---|---|
| PySpark as primary pipeline | Done | `01_pipeline.py` executed in CI and Databricks; primary Delta tables queried successfully. |
| Modular, documented notebooks | Partial | Setup, primary processing, and sensitivity are separated into three documented notebooks. Primary parsing/validation/join logic remains within one notebook; no independently packaged transformation library. Research SQL and reference calculations are separate modules. |
| Description before each code section | Done | Notebook sections and analysis stages have explanatory comments/Markdown. No formal style linter enforces this. |
| Five-character FIPS strings | Done | Normalization and invalid-key checks implemented. Geography differences and alias duplicates documented. |
| Suppressed overdose values remain missing | Done | Source blank/suppression handling, strict-window rules, and independent reference tests; literal reported zeros preserved. |
| Investigate December, quarterly, rolling approaches | Partial | December, quarter-end means, monthly means, and trailing-three means implemented and compared. Live annual comparison SQL verified; full monthly/quarterly PySpark outputs tested locally. Their five Delta output tables still need notebook execution/readback in Databricks. |
| Never sum overlapping 12-month-ending counts | Done | Snapshot selection and AVG used across windows. Sums of observed counts are across counties for a selected annual measure, or across non-overlapping calendar years when explicitly selected in the original dashboard; neither constructs annual deaths from monthly windows. |
| Never zero-fill suppression | Done | Missing measures and coverage flags retained; zero preservation tested. |
| Distinguish reported and derived/imputed values | Done | December classified as reported; smoothing classified as derived means, not annual death estimates; no analyst imputation. CDC dispensing rates are explicitly identified as source estimates. |
| Validate integrated county-year data | Partial | Structural and numeric checks pass; five of eight historical targets match. Three differences remain unexplained, so historical replication is incomplete. |
| Interactive dashboard | Done | Existing two-page draft with user-reported acceptance/review. No independent browser acceptance test; publication is separate. |
| Pipeline architecture diagram | Done | Mermaid architecture in `architecture.md`. No exported image required or fabricated. |
| Automated data-quality checks and documentation | Done | CI source/hash checks, Spark execution, persisted local tables, strict-window checks, statistical reference tests, and quality documentation. CI does not verify Unity Catalog/Delta behavior or browser rendering. |

## Dashboard requirements

| View/control | Status | Evidence/qualification |
|---|---|---|
| Dispensing trends | Done | Original page, unweighted county rate means; not national rates. |
| Overdose trends | Done | Reported December subtotals plus coverage; not population-adjusted rates. |
| Geographic differences | Done | State comparisons and county detail/filter views; no county choropleth or spatial model is claimed. |
| County and state comparisons | Done | Original state charts and county details; limited by suppression and county population. |
| Dispensing–overdose relationships | Done | Original scatter plot; research additionally provides Pearson/Spearman by year/cohort/method. |
| Missing-data patterns | Done | Original missingness charts; sensitivity coverage and missingness comparisons. |
| Year, state, county filters | Done | Original filters explicitly confirmed by user. Sensitivity filters were added and the user reported reviewing that page; no individual automated filter assertions. |
| Annualization sensitivity | Done | Additional draft page; live SQL query results verified and reviewed by user. Full persisted sensitivity outputs are a separate remaining deployment step. |

## Research questions and safeguards

| Requirement | Status | Evidence/qualification |
|---|---|---|
| Association between dispensing and overdose | Done | 60 year/cohort/method summaries with Pearson and tie-adjusted Spearman; independently reproduced. Unadjusted descriptive associations only. |
| Changes from 2020–2024 | Done | Available/shared/fixed cohort means and changes; fixed-cohort endpoint direction differs across time summaries. |
| Geographic variation | Partial | 255 state-year descriptive/coverage summaries and county dashboard details. No formal county spatial analysis or population-adjusted risk analysis. Existing scope is descriptive. |
| Avoid causal claims about legally dispensed opioids | Done | Report/dashboard limitations distinguish dispensing from all-drug mortality and legal/illegal channels. |
| Dashboard first | Done | Dashboard created/reviewed before research expansion. |
| No unexplained extra datasets | Done | Only the two supplied CDC snapshots used. No population or boundary dataset added. |
| Document limitations/transforms | Done | Source inspection, methods, sensitivity, quality, findings, report draft, manifest, and runbook. Original-source provenance remains incomplete. |
| GitHub version control and incremental tests | Done | Repository commits and passing workflows; no credentials stored in project files. |
| No fabricated outputs/screenshots | Done | Full query exports and independently checked numerical findings; no screenshots claimed. |

## Historical validation targets

| Metric | Current | Prior target | Status |
|---|---:|---:|---|
| Raw dispensing | 18,864 | 18,864 | Match |
| Raw overdose | 226,368 | 226,368 | Match |
| Matching county FIPS | 3,142 | 3,142 | Match |
| Common county-years | 15,710 | 15,710 | Match |
| Complete observations | 8,203 | 8,180 | Open: +23 |
| Complete-case counties | 2,388 | 2,385 | Open: +3 |
| Missing dispensing | 297 | 297 | Match |
| Missing overdose | 7,275 | 7,298 | Open: −23 |

No tolerance was pre-agreed that makes the differences acceptable. Source revisions and old processing rules are hypotheses, not established explanations. Previous pandas code/source release is needed for a row-level reconciliation.

## Final deliverables and submission gaps

| Deliverable | Status | Remaining action |
|---|---|---|
| Working Databricks primary pipeline | Done | Primary outputs verified; capture managed runtime/job details for stronger handoff evidence. |
| Working interactive dashboard | Done | User-reviewed draft. Confirm final audience and publication if required; no claim it is published. |
| Reproducible code | Partial | Frozen snapshots, checksums, CI, exact queries/results and runbook available. Exact export/download and snapshot release history and managed runtime metadata remain missing. CI dependency is pinned but not a full lockfile. |
| Data-quality documentation | Done | Structural checks, coverage, suppression, aliases, geography, target differences documented. Full resolution of discrepancies remains open. |
| Pipeline diagram | Done | Mermaid source updated for current architecture. |
| Final capstone report | Partial | Draft in `capstone_report.md`, based on verified findings. Verified CDC source citations added; still needs student/course/advisor details, exact snapshot release history, citation-style/rubric alignment, and academic review. |
| Presentation | Open | No slide deck requested or created in this increment. |

## Recommended closeout order

1. Run and read back `02_sensitivity.py` on Databricks Delta; retain execution evidence.
2. Supply exact export/download and snapshot release history plus the previous pandas implementation, then reconcile or formally document benchmark differences.
3. Review the report draft and add university-required front matter, citations, and formatting.
4. Decide dashboard audience/publication and prepare the final presentation if required.

## Source documentation update

The user supplied both CDC source pages, verified November 13, 2026. Publication titles, dispensing units/source-estimation basis, prescriber-versus-resident geography, mortality windows, suppression rules, and mortality dataset ID are now documented in `source_citations.md`. Source landing-page identification is complete. Exact original export/download and uploaded-release provenance remain open. These links do not explain the historical 23-observation discrepancy.
