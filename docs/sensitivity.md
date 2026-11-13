# Annualization sensitivity methods

## Definitions

All inputs are reported 12-month-ending overdose counts, 2020–2024. None of the smoothed measures is an estimate of annual deaths; they are derived summaries of reported snapshots. No imputation is performed.

| Method | Required snapshots | Output interpretation |
|---|---|---|
| `december` | December | Reported 12-month-ending count at year end |
| `quarter_end_mean_4` | March, June, September, December | Mean burden across quarter-end snapshots; not quarterly deaths |
| `monthly_mean_12` | January through December | Mean burden across monthly snapshots; not annual deaths |
| `december_trailing_mean_3` | October, November, December | December endpoint of trailing three-month mean |

A strict mean is null unless all constituent months are present and reported. Observed-period counts are retained so coverage losses are inspectable. Missingness includes reported suppression and, where applicable, absent source periods. No suppressed value becomes zero. Literal reported zeros remain zero. No operation adds counts across overlapping time windows to construct deaths; means use Spark AVG.

`overdose_quarterly` retains quarter-end snapshots separately. `overdose_rolling3` contains trailing three-calendar-month means throughout the analysis period, including cross-year windows. January and February 2020 cannot have complete three-month windows because the source begins in January 2020. Calendar range windows do not replace missing months with older observations.

## Cohort comparison

The annual comparison is restricted to the primary common-key county-year universe. Three summary cohorts are retained:

- `available`: all eligible county-years; each method has its own observed/complete coverage.
- `common_within_year`: counties with dispensing and all four overdose measures available in that year.
- `common_all_years`: counties satisfying all four methods and dispensing in every year from 2020 through 2024.

Summaries include eligible, observed and complete county-year counts, unweighted mean county overdose measures, and exploratory Pearson correlations between dispensing and the overdose measure on complete pairs. Correlations of rates with counts are affected by population size and are ecological, not causal. No population-adjusted mortality comparison is possible with the present data. No statistical significance or causal claim is implied. Fixed cohorts improve comparability but can overrepresent large, consistently reporting counties.

Pairwise differences compare each alternate method with December using exactly the same complete county-year pairs. Each method can have a different paired cohort; the common-cohort summaries address that limitation.

## Outputs and execution

Import `notebooks/02_sensitivity.py` into Databricks and Run all after the primary setup. Defaults read the existing `/Volumes/workspace/capstone/source_files/overdose.csv` and `workspace.capstone.county_year_common`. It writes five separate Delta tables: `overdose_quarterly`, `overdose_rolling3`, `sensitivity_county_year`, `sensitivity_summary`, and `sensitivity_paired`. Primary dashboard tables are left unchanged.

GitHub Actions runs the same notebook with local Spark/Parquet, then compares every annual county-method result against independent CSV calculations. It also verifies suppressed windows remain null and rolling means handle the calendar-year boundary correctly. Databricks execution of this new notebook and dashboard integration of these sensitivity tables are separate steps.

## Verified coverage findings

The live read-only SQL dataset ran successfully in the connected Databricks workspace. Its full 20-row coverage result is saved in `sensitivity_coverage.csv`. These are computed observations, not validation targets.

| Complete county-year pairs | 2020 | 2024 |
|---|---:|---:|
| December | 1,588 | 1,562 |
| December trailing three-month mean | 1,490 | 1,459 |
| Four quarter-end mean | 1,251 | 1,285 |
| Twelve-month snapshot mean | 1,177 | 1,234 |

865 counties have dispensing and all four measures available in every year. The within-year common cohort has 1,177, 1,282, 1,330, 1,348, and 1,234 counties for 2020 through 2024 respectively. Smoothing therefore changes sample availability materially. These coverage results alone do not establish whether substantive trend or association conclusions are robust.

## Dashboard deployment

A new **Annualization sensitivity** page was appended to the existing draft, preserving the user-confirmed original page and selected warehouse. It contains method coverage, available-case means, within-year common-cohort means, fixed-cohort means, paired differences, missingness, details, and year/state/county filters. The dashboard queries the existing source Volume read-only through `dashboard/sensitivity_dataset.sql`, so it does not require a manual notebook run to display these annual comparisons. The full PySpark notebook additionally produces quarter-end and monthly rolling outputs when executed in Databricks. Those five persisted sensitivity tables have only been exercised with local Spark/Parquet so far, not Databricks Delta.

The new page is saved as a draft, not published. Its SQL was validated; browser rendering and filter interactions on this new page still require acceptance. The original dashboard acceptance does not cover this page. Using a live source query means Volume permissions are required for viewers; do not assume primary-table access alone is sufficient. The source snapshot and primary tables must correspond to the same release; rerun validation before replacing either.
