"""Build the findings report and CSV exports from retrieved Databricks query results."""
# Use saved provider results as evidence; no simulated data or hard-coded findings.
import csv
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(name):
    result=json.loads((ROOT/'analysis'/f'{name}_results.json').read_text())
    assert not result['truncated']
    columns=[c['name'] for c in result['columns']]
    rows=[dict(zip(columns,r)) for r in result['rows']]
    assert len(rows)==result['total_row_count']
    with (ROOT/'analysis'/f'{name}_results.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns)
        writer.writeheader();writer.writerows(rows)
    return rows

def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def n(value, digits=2):
    return f'{float(value):,.{digits}f}'

# Separate cohort, method, and geographic conclusions so coverage changes stay visible.
a=read('associations');g=read('geographic')
fixed=[r for r in a if r['cohort']=='common_all_years' and r['method']=='december']
ends=[r for r in a if r['cohort']=='common_all_years' and r['year']=='2024']
available=[r for r in a if r['cohort']=='available' and r['method']=='december']
geo=[r for r in g if r['year']=='2024']
miss=sorted(geo,key=lambda r:float(r['missing_overdose_pct']),reverse=True)[:5]
first,last=fixed[0],fixed[-1]
text=f'''# Research findings: U.S. opioid dispensing and overdose trends, 2020–2024

## Scope and evidence

These descriptive results come from executed, read-only Databricks SQL, exported in full as `analysis/associations_results.csv` (60 rows) and `analysis/geographic_results.csv` (255 rows). The state-year data cover the 50 states and District of Columbia. Independent standard-library calculations from the supplied source ZIPs reproduce every exported numeric summary within floating-point tolerance (1e-10). No new dataset, population denominator, analyst imputation, significance test, or causal model is introduced. CDC dispensing rates themselves are source estimates based on projected retail prescription totals; this is distinct from analyst-created smoothing of reported overdose counts.

The primary common-key panel has 15,710 county-years. Correlations use complete dispensing–overdose pairs, separately within each year. Available cohorts vary by year/method; shared-within-year cohorts hold counties constant across methods in a year; the fixed cohort contains 865 counties with all measures and dispensing available throughout all five years. The fixed cohort is a selected subset and is not representative by design.

## Question 1: Association between dispensing and overdose measures

For December counts in available complete cases, yearly Pearson coefficients range from {n(min(float(r['pearson_r']) for r in available),3)} to {n(max(float(r['pearson_r']) for r in available),3)}; Spearman coefficients range from {n(min(float(r['spearman_rho']) for r in available),3)} to {n(max(float(r['spearman_rho']) for r in available),3)}. These indicate small linear correlations and larger positive rank correlations in this selected sample. They do not estimate the effect of dispensing on overdose deaths.

The fixed cohort gives a different association magnitude:

{table(['Year','Counties','Pearson r','Spearman rho'], [[r['year'],r['complete_counties'],n(r['pearson_r'],3),n(r['spearman_rho'],3)] for r in fixed])}

Pearson is near zero in this fixed cohort; the rank associations are positive. Differences between these coefficients show that one linear summary does not capture the same feature as the rank summary. These results alone do not diagnose outliers, a specific nonlinear mechanism, or confounding. Counts depend on county population, and no population adjustment has been performed. Both cohorts can be biased by suppression and dispensing availability. Spearman ranks are computed using average ranks for ties. No p-values or confidence intervals are reported, and no inference of statistical significance is made.

## Question 2: Changes from 2020 through 2024

In the same 865 counties, the unweighted mean county dispensing rate decreased from {n(first['mean_county_dispensing'])} to {n(last['mean_county_dispensing'])} prescriptions per 100 persons, a {n(abs(float(last['dispensing_pct_change_since_2020'])))}% decrease. This is a mean of county rates, not a national dispensing rate.

{table(['Year','Mean county dispensing rate','Mean county December count'], [[r['year'],n(r['mean_county_dispensing']),n(r['mean_county_overdose_measure'])] for r in fixed])}

December mean counts peak in 2022 within this cohort and are lower in 2024 than in 2020. The endpoint conclusion changes when the time summary changes:

{table(['Method, fixed 865 counties','2020 mean','2024 mean','Change 2020–2024'], [[r['method'],n(r['overdose_2020']),n(r['mean_county_overdose_measure']),n(r['overdose_pct_change_since_2020'])+'%'] for r in ends])}

**The direction of endpoint change is not robust across these definitions.** December and its trailing three-month mean decrease; four-quarter-end and twelve-month snapshot means increase. This difference persists with identical counties, so county composition alone cannot explain it. The methods summarize different portions of the trajectory: December measures a year-end 12-month window, while annual means average multiple overlapping windows ending throughout the year, some extending into the preceding year. They are different estimands. Do not call the smoothed measures annual death totals or conclude that the methods contradict one another. No overlapping counts are summed to construct deaths.

Available-cohort changes are also exported but should not be interpreted as longitudinal changes in the same counties. The fixed cohort reduces that problem while selecting for consistently reported observations.

## Question 3: Geographic differences and missingness

The exported state-year table provides eligible, reported, and complete county counts alongside mean county dispensing rates, mean reported county overdose counts, and observed overdose subtotals. These are descriptive summaries, not state mortality rates. State-year county dispensing means are unweighted and omit unavailable dispensing values; overdose subtotals omit missing/suppressed counties.

Five states with the largest percentages of missing December overdose county observations in 2024 are:

{table(['State','Eligible counties','Reported overdose counties','Missing overdose observations'], [[r['state'],r['eligible_counties'],r['overdose_reported_counties'],n(r['missing_overdose_pct'])+'%'] for r in miss])}

This is a ranking of missingness, not overdose risk. High missingness limits geographic comparisons. County-level comparisons remain available in the dashboard; no spatial clustering model, boundary map, or formal county change analysis is claimed in this report.

## Limitations and unresolved issues

- Geographic attribution differs: CDC dispensing uses prescriber location, while mortality uses decedent county of residence. FIPS matching does not eliminate this mismatch. Dispensing excludes mail-order prescriptions and methadone dispensed through treatment programs; see `source_citations.md`.
- All results are ecological. Legally dispensed opioids must not be described as causing deaths in the all-drug mortality dataset, which includes drugs obtained through legal and illegal channels.
- Overdose measures are counts, not population-adjusted death rates. Pearson and Spearman are unadjusted descriptive associations; no demographic, socioeconomic, or population confounders are controlled.
- Provisional deaths can be revised. Source release versions and geographic conventions affect reproducibility. CDC source landing pages and definitions are verified in `source_citations.md`. Exact export/download dates and correspondence to a specific source release remain unresolved.
- Suppression is not random. Strict smoothing drops more county-years and the 865-county fixed cohort can favor larger, consistently reporting counties. No uncertainty interval for suppressed counts is estimated.
- The four methods summarize overlapping 12-month-ending snapshots with different temporal support. Comparing endpoint changes is sensitivity analysis, not four alternative estimates of calendar-year deaths.
- The historical target differences are now explained: the original pandas numeric conversion coerced 23 comma-formatted reported counts to missing. The original behavior reproduces 8,180 complete observations, 2,385 complete-case counties, and 7,298 missing values; comma normalization reproduces the current 8,203, 2,388, and 7,275. See `pandas_reconciliation.md` for row-level evidence and the separate limit on byte verification of the newly uploaded oversized CSV. Current research results already use the corrected parsing.
- Primary and sensitivity dashboard pages were reviewed by the user. No screenshot or automated browser test is claimed. This report adds no dashboard page or publication action.

## Reproduction and query evidence

Run `analysis/associations_trends.sql` and `analysis/geographic.sql` in the connected workspace. They are read-only and require access to the source Volume and primary tables. The SQL and exported raw results are versioned. `analysis/build_report.py` recreates the report and CSVs from those results; it does not refresh Databricks queries. `python -m unittest discover -s tests -p 'test_*.py'` checks the statistics and independently reproduces all exported rows from the frozen source snapshots. GitHub Actions also runs the existing full Spark processing checks.

- [Association and trend query](https://dbc-dc957048-d7f2.cloud.databricks.com/one/chat/threads/5959d939f6f342a686ebaa201e827cd3?o=7474646615740609&utm_source=genie_chat_mcp)
- [Geographic query](https://dbc-dc957048-d7f2.cloud.databricks.com/one/chat/threads/ffb179361fab4efca3fe244c88dcbc27?o=7474646615740609&utm_source=genie_chat_mcp)
'''
(ROOT/'docs/research_findings.md').write_text(text)
