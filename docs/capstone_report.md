# U.S. Opioid Dispensing and Overdose Trends, 2020–2024

**Graduate Data Science Capstone — Report Draft**  
Saint Peter's University  
Author, course, advisor, and submission date: **to be supplied**  
Status: research draft for academic review; source citations and final formatting are incomplete.

## Abstract

This project develops a reproducible county-level pipeline and interactive dashboard examining opioid dispensing and provisional all-drug overdose counts in the United States during 2020–2024. Two supplied CDC snapshots contain 18,864 dispensing records and 226,368 monthly mortality records before period restriction. PySpark normalizes county FIPS, retains suppression as missing, resolves identical analytic aliases, and integrates 15,710 common county-year observations. December counts are compared with strict quarter-end, monthly, and trailing-three-month snapshot means. Associations are summarized using yearly Pearson and tie-adjusted Spearman correlations; shared cohorts address differences in data availability. A fixed cohort of 865 counties shows a 17.58% decline in mean county dispensing and a 14.12% decline in mean December overdose counts from 2020 to 2024. In contrast, its mean of monthly snapshots increases 10.96%. Thus, endpoint trend direction depends on temporal definition even with fixed counties. Findings are descriptive ecological associations, not causal effects or population-adjusted mortality risks. Suppression, provisional revisions, incomplete source provenance, and unresolved historical validation differences limit interpretation.

## 1. Introduction and objectives

The project examines how county-level opioid dispensing and reported overdose measures vary together, over time, and geographically. Comparing these sources requires explicit decisions about geography, suppression, and time windows. A 12-month-ending count reported in a month overlaps counts reported in adjacent months; adding those observations would double-count events. Missing or suppressed counts must not be interpreted as zero.

The research questions are:

1. What association exists between county-level opioid dispensing rates and drug overdose deaths?
2. How have dispensing rates and overdose measures changed from 2020 through 2024?
3. How do descriptive patterns and data availability vary geographically across U.S. counties?

The mortality measure is all-drug overdose, not a measure attributable exclusively to legally dispensed opioids. The project does not test whether legal dispensing caused the reported deaths. No additional explanatory or population dataset is introduced.

## 2. Data and study scope

The source descriptions supplied for the project are CDC county-level dispensing rates, 2019–2024 [1], and provisional county-level overdose deaths, 2020–2025 [2]. The common analysis period is 2020–2024. Source titles in this draft are descriptive, not complete bibliographic citations. Original download URLs, download dates, and formal release identifiers remain unknown. The mortality CSV contains `Data as of` text `07/05/2026`; it is preserved verbatim and is not treated as a download date.

| Source | Core fields used | Important interpretation |
|---|---|---|
| Dispensing [1] | Location, Year, STATE_NAME, Opioid Dispensing Rate | Numeric county rate; the similarly named display-bin column is not used as a numeric measure. Source documentation should confirm the per-100-person unit in the final citation. |
| Overdose [2] | FIPS, Year, Month, Provisional Drug Overdose Deaths | Reported provisional 12-month-ending counts; blank cells with suppression footnotes remain missing. Literal zeros remain zero. |

The dispensing snapshot has 3,144 distinct county FIPS. The overdose snapshot has 3,142 distinct FIPS, with two Virginia name-alias pairs sharing FIPS and identical analytic observations. The common county set includes 3,142 FIPS; dispensing-only FIPS 02063 and 02066 are retained in the full dashboard coverage panel but excluded from common-key research comparisons. No geographic reassignment or historical boundary crosswalk is applied. The state-year summaries cover the 50 states and District of Columbia.

## 3. Pipeline and reproducibility

The development workflow is **GitHub → Codex → Databricks → Dashboard**. GitHub stores source snapshots, notebooks, queries, tests, result exports, and documentation. Codex maintains these artifacts and runs checks. Databricks Free Edition executes the primary PySpark pipeline and SQL queries. Databricks AI/BI provides interactive year, state, and county filtering.

Processing stages are:

1. Verify source archive/CSV hashes and retain original source strings.
2. Normalize FIPS to five-character strings and parse year/month and numeric values conservatively.
3. Reject malformed keys and unrecognized values; collapse identical analytic aliases and reject conflicting duplicates.
4. Restrict the analysis period and select December's reported count for the primary county-year analysis.
5. Produce a full coverage panel and a separate common-key panel with missingness and complete-case flags.
6. Compare computed quality metrics with historical targets without forcing agreement.
7. Compute strict annualization comparisons, explicit cohorts, and descriptive research summaries.
8. Save query evidence and build the dashboard with coverage and interpretation notes.

The architecture diagram is in `docs/architecture.md`. Primary tables have executed successfully in Databricks and have been queried. The separate sensitivity PySpark notebook has been exercised with local Spark/Parquet; its five additional Delta output tables still require Databricks execution evidence. The sensitivity dashboard and research SQL already run directly against the source Volume and primary tables and do not depend on those unexecuted Delta tables.

Local/CI verification uses Python 3.12, Java 21, and PySpark 4.0.1. Snapshot hashes and the primary bootstrap's historical artifact pin make source/code identity explicit. The exact managed Databricks runtime version was not recorded. GitHub Actions validates source hashes, Python syntax, Spark execution, suppression/calendar logic, statistical reference calculations, and all exported research summaries. It does not prove Unity Catalog permissions, Delta behavior for the pending tables, or browser rendering. User-reported dashboard acceptance is recorded separately.

## 4. Analytical methods

The unit of analysis is the county-year. Annual dispensing is paired with four overdose definitions:

| Method | Required reported snapshots | Interpretation |
|---|---|---|
| December | December | Reported year-end 12-month count |
| Quarter-end mean | March, June, September, December | Derived mean of four overlapping snapshots |
| Monthly mean | All 12 months | Derived mean of monthly snapshots |
| December trailing mean | October, November, December | Derived three-month snapshot mean |

A derived mean is missing if any required observation is missing or suppressed. It is not an imputed count or annual death total. The separate rolling series uses three-calendar-month windows, including cross-year windows; January/February 2020 lack complete prior windows in the supplied source.

Three cohorts are compared: method-specific available complete cases, common counties across all methods within a year, and the fixed 865-county cohort complete across all methods and five years. The fixed cohort improves longitudinal comparability but may select larger or consistently reporting counties. Cohort membership is determined before dashboard selection filters.

Pearson measures linear association. Spearman is Pearson correlation of average ranks, with ties handled explicitly. Correlations are computed separately for each year, method, and cohort; repeated county observations are not pooled into a single cross-year correlation. County means are unweighted. Percent changes compare each summary with its own 2020 baseline; available-cohort changes can reflect changing membership. No p-values, confidence intervals, covariate-adjusted regression, or causal effect estimates are reported.

State summaries show observed county coverage, unweighted county dispensing means, mean reported county counts, and reported overdose subtotals. These are not state dispensing rates or mortality rates. No spatial inference or population-standardized comparison is performed.

## 5. Results

The common-key panel contains 15,710 county-years, including 8,203 complete observations across 2,388 counties. It contains 297 missing dispensing values and 7,275 missing/suppressed overdose values. Five historical validation targets match exactly; three remain unresolved and are shown in the requirements audit. All 60 association/trend rows and 255 state-year rows below were exported from executed Databricks queries and independently reproduced from the frozen source snapshots.

### Research question 1: Association between dispensing and overdose measures

For December counts in available complete cases, yearly Pearson coefficients range from 0.046 to 0.085; Spearman coefficients range from 0.344 to 0.390. These indicate small linear correlations and larger positive rank correlations in this selected sample. They do not estimate the effect of dispensing on overdose deaths.

The fixed cohort gives a different association magnitude:

| Year | Counties | Pearson r | Spearman rho |
|---|---|---|---|
| 2020 | 865 | 0.002 | 0.153 |
| 2021 | 865 | 0.014 | 0.195 |
| 2022 | 865 | 0.015 | 0.208 |
| 2023 | 865 | 0.003 | 0.196 |
| 2024 | 865 | -0.014 | 0.182 |

Pearson is near zero in this fixed cohort; the rank associations are positive. Differences between these coefficients show that one linear summary does not capture the same feature as the rank summary. These results alone do not diagnose outliers, a specific nonlinear mechanism, or confounding. Counts depend on county population, and no population adjustment has been performed. Both cohorts can be biased by suppression and dispensing availability. Spearman ranks are computed using average ranks for ties. No p-values or confidence intervals are reported, and no inference of statistical significance is made.

### Research question 2: Changes from 2020 through 2024

In the same 865 counties, the unweighted mean county dispensing rate decreased from 47.35 to 39.02 prescriptions per 100 persons, a 17.58% decrease. This is a mean of county rates, not a national dispensing rate.

| Year | Mean county dispensing rate | Mean county December count |
|---|---|---|
| 2020 | 47.35 | 93.61 |
| 2021 | 45.91 | 107.95 |
| 2022 | 43.04 | 109.15 |
| 2023 | 40.84 | 106.58 |
| 2024 | 39.02 | 80.39 |

December mean counts peak in 2022 within this cohort and are lower in 2024 than in 2020. The endpoint conclusion changes when the time summary changes:

| Method, fixed 865 counties | 2020 mean | 2024 mean | Change 2020–2024 |
|---|---|---|---|
| december | 93.61 | 80.39 | -14.12% |
| december_trailing_mean_3 | 92.45 | 82.50 | -10.76% |
| monthly_mean_12 | 84.18 | 93.41 | 10.96% |
| quarter_end_mean_4 | 85.95 | 91.20 | 6.10% |

**The direction of endpoint change is not robust across these definitions.** December and its trailing three-month mean decrease; four-quarter-end and twelve-month snapshot means increase. This difference persists with identical counties, so county composition alone cannot explain it. The methods summarize different portions of the trajectory: December measures a year-end 12-month window, while annual means average multiple overlapping windows ending throughout the year, some extending into the preceding year. They are different estimands. Do not call the smoothed measures annual death totals or conclude that the methods contradict one another. No overlapping counts are summed to construct deaths.

Available-cohort changes are also exported but should not be interpreted as longitudinal changes in the same counties. The fixed cohort reduces that problem while selecting for consistently reported observations.

### Research question 3: Geographic differences and missingness

The exported state-year table provides eligible, reported, and complete county counts alongside mean county dispensing rates, mean reported county overdose counts, and observed overdose subtotals. These are descriptive summaries, not state mortality rates. State-year county dispensing means are unweighted and omit unavailable dispensing values; overdose subtotals omit missing/suppressed counties.

Five states with the largest percentages of missing December overdose county observations in 2024 are:

| State | Eligible counties | Reported overdose counties | Missing overdose observations |
|---|---|---|---|
| Mississippi | 82 | 22 | 73.17% |
| Arkansas | 75 | 22 | 70.67% |
| Wisconsin | 72 | 23 | 68.06% |
| Colorado | 64 | 21 | 67.19% |
| Wyoming | 23 | 8 | 65.22% |

This is a ranking of missingness, not overdose risk. High missingness limits geographic comparisons. County-level comparisons remain available in the dashboard; no spatial clustering model, boundary map, or formal county change analysis is claimed in this report.

## 6. Limitations and unresolved issues

- All results are ecological. Legally dispensed opioids must not be described as causing deaths in the all-drug mortality dataset, which includes drugs obtained through legal and illegal channels.
- Overdose measures are counts, not population-adjusted death rates. Pearson and Spearman are unadjusted descriptive associations; no demographic, socioeconomic, or population confounders are controlled.
- Provisional deaths can be revised. Source release versions and geographic conventions affect reproducibility. The original CDC download URLs and complete provenance remain to be supplied.
- Suppression is not random. Strict smoothing drops more county-years and the 865-county fixed cohort can favor larger, consistently reporting counties. No uncertainty interval for suppressed counts is estimated.
- The four methods summarize overlapping 12-month-ending snapshots with different temporal support. Comparing endpoint changes is sensitivity analysis, not four alternative estimates of calendar-year deaths.
- The historical targets still differ: 8,203 versus 8,180 complete observations, 2,388 versus 2,385 complete-case counties, and 7,275 versus 7,298 missing overdose observations. The cause is unresolved; the previous pandas code/source release is needed for reconciliation.
- Primary and sensitivity dashboard pages were reviewed by the user. No screenshot or automated browser test is claimed. This report adds no dashboard page or publication action.



## 7. Discussion and conclusion

Dispensing decreased in the fixed cohort, while the interpretation of overdose endpoint change depends on the time summary. December and annual averages of overlapping windows answer different temporal questions. Presenting them as interchangeable annual totals would obscure an important sensitivity result. Associations also depend on the chosen correlation and cohort, reinforcing the need to show sample selection and data coverage alongside statistical summaries.

The project delivers a functioning primary pipeline, user-reviewed interactive dashboard, reproducible descriptive analyses, and explicit limitations. It supports cautious exploration of county-level patterns, not attribution of all-drug overdose deaths to legal opioid dispensing. Further modeling would need a separately justified design and potentially population data; neither is assumed necessary or completed here.

Before submission, complete provenance, reconcile or formally explain benchmark discrepancies, execute/read back the remaining sensitivity Delta tables, add author/course/advisor details and university-required citations/formatting, and obtain academic review. Dashboard publication and presentation creation remain separate decisions.

## 8. Data references and project artifacts

[1] Centers for Disease Control and Prevention. County-level opioid dispensing data, 2019–2024. Supplied file `opioid_dispensing_2026_update.csv`; exact formal title, original URL, release identifier, and access date pending. Archived as `sources/dispensing.csv.zip`; hashes and schema in `sources/manifest.json`.

[2] Centers for Disease Control and Prevention. Provisional county-level drug overdose death data, 2020–2025. Supplied file `overdose_deaths_2026_update.csv` in ZIP; exact formal title, original URL, release identifier, and access date pending. Archived as `sources/overdose.csv.zip`; hashes and schema in `sources/manifest.json`.

Project code: https://github.com/dheritageprojects/DS670Capstone

Full reproduction instructions: `docs/reproducibility.md`. Requirements status: `docs/requirements_audit.md`. Numerical evidence: `analysis/associations_results.json`, `analysis/geographic_results.json`, their CSV exports, and `docs/sensitivity_coverage.csv`. No fabricated source citation, literature review, screenshot, or result is included.
