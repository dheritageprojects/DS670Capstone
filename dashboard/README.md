# Databricks AI/BI dashboard

[Open the existing dashboard draft](https://dbc-dc957048-d7f2.cloud.databricks.com/sql/dashboardsv3/01f1df0509d010f987459df183dcdd91?o=7474646615740609).

The original page and year/state/county filters were explicitly confirmed working by the user. The user subsequently reported reviewing the sensitivity page, with no failure reported. This is user-reported acceptance/review, not an automated browser test or a fabricated screenshot. The last saved asset was a draft; publication/audience still needs a separate decision and readback.

## Pages and data

| Page | Data | Views |
|---|---|---|
| County trends and coverage | `workspace.capstone.county_year`, `quality_report` | Dispensing/overdose trends, reporting coverage, state comparisons, scatter plot, missingness, county details, unfiltered validation report |
| Annualization sensitivity | `sensitivity_dataset.sql`: source Volume plus `county_year_common` | Four method comparisons, complete coverage, available/shared/fixed cohort means, paired differences, missingness, detail table |

Each page has year, state, and county FIPS controls for its analytical dataset. The quality-report dataset remains unfiltered. County labels are FIPS identifiers. State bars and county details satisfy descriptive geography; no county map, boundary dataset, or spatial inference has been added.

## Reproduction and safeguards

The current complete definition is `opioid_trends.lvdash.json`; deployment identifiers and last-known warehouse are in `deployment.json`. Prefer the existing asset over duplicate creation. `build_dashboard.py` recreates only the original baseline and would omit later additions if used as a replacement. `build_sensitivity.py` appends a page to a freshly exported baseline and refuses one that already contains it. Read a current draft and preserve user edits/etag before updating.

Source selection is deliberate: the original dashboard uses the full coverage panel, including dispensing-only county keys. Research and sensitivity use common-key observations. Historical target differences are displayed, not hidden. The live sensitivity dataset does not require the separate five sensitivity Delta tables; their Databricks Delta execution and readback are now verified in `docs/sensitivity_verification.md`.

Unweighted county dispensing means are not statewide/national dispensing rates. Reported overdose subtotals omit missing counties and vary with coverage; they are not national totals or population-adjusted death rates. No suppressed value is zero-filled. Smoothing averages overlapping snapshots and is not an estimate of annual deaths. The sensitivity page labels these definitions and cohort restrictions explicitly.

After any update, recheck charts, nulls, units, filter propagation, sparse selections, and the intended warehouse. Sensitivity viewers also need Volume access, not only table access. See `docs/dashboard_acceptance.md`, `docs/sensitivity.md`, and `docs/reproducibility.md` for evidence and remaining limitations. Publishing and credential-embedding choices are separate actions, not implied by creation or review.
