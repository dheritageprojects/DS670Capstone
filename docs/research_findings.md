# Research findings: U.S. opioid dispensing and overdose trends, 2020–2024

## Scope and evidence

These descriptive results come from executed, read-only Databricks SQL, exported in full as `analysis/associations_results.csv` (60 rows) and `analysis/geographic_results.csv` (255 rows). The state-year data cover the 50 states and District of Columbia. Independent standard-library calculations from the supplied source ZIPs reproduce every exported numeric summary within floating-point tolerance (1e-10). No new dataset, population denominator, imputation, significance test, or causal model is introduced.

The primary common-key panel has 15,710 county-years. Correlations use complete dispensing–overdose pairs, separately within each year. Available cohorts vary by year/method; shared-within-year cohorts hold counties constant across methods in a year; the fixed cohort contains 865 counties with all measures and dispensing available throughout all five years. The fixed cohort is a selected subset and is not representative by design.

## Question 1: Association between dispensing and overdose measures

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

## Question 2: Changes from 2020 through 2024

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

## Question 3: Geographic differences and missingness

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

## Limitations and unresolved issues

- All results are ecological. Legally dispensed opioids must not be described as causing deaths in the all-drug mortality dataset, which includes drugs obtained through legal and illegal channels.
- Overdose measures are counts, not population-adjusted death rates. Pearson and Spearman are unadjusted descriptive associations; no demographic, socioeconomic, or population confounders are controlled.
- Provisional deaths can be revised. Source release versions and geographic conventions affect reproducibility. The original CDC download URLs and complete provenance remain to be supplied.
- Suppression is not random. Strict smoothing drops more county-years and the 865-county fixed cohort can favor larger, consistently reporting counties. No uncertainty interval for suppressed counts is estimated.
- The four methods summarize overlapping 12-month-ending snapshots with different temporal support. Comparing endpoint changes is sensitivity analysis, not four alternative estimates of calendar-year deaths.
- The historical targets still differ: 8,203 versus 8,180 complete observations, 2,388 versus 2,385 complete-case counties, and 7,275 versus 7,298 missing overdose observations. The cause is unresolved; the previous pandas code/source release is needed for reconciliation.
- Primary and sensitivity dashboard pages were reviewed by the user. No screenshot or automated browser test is claimed. This report adds no dashboard page or publication action.

## Reproduction and query evidence

Run `analysis/associations_trends.sql` and `analysis/geographic.sql` in the connected workspace. They are read-only and require access to the source Volume and primary tables. The SQL and exported raw results are versioned. `analysis/build_report.py` recreates the report and CSVs from those results; it does not refresh Databricks queries. `python -m unittest discover -s tests -p 'test_*.py'` checks the statistics and independently reproduces all exported rows from the frozen source snapshots. GitHub Actions also runs the existing full Spark processing checks.

- [Association and trend query](https://dbc-dc957048-d7f2.cloud.databricks.com/one/chat/threads/5959d939f6f342a686ebaa201e827cd3?o=7474646615740609&utm_source=genie_chat_mcp)
- [Geographic query](https://dbc-dc957048-d7f2.cloud.databricks.com/one/chat/threads/ffb179361fab4efca3fe244c88dcbc27?o=7474646615740609&utm_source=genie_chat_mcp)
