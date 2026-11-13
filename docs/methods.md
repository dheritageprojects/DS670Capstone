# Methods and limitations

## Annual alignment

The first dashboard uses December observations of reported 12-month-ending overdose deaths, aligned to annual dispensing for 2020–2024. December values can be missing or suppressed. Preserve them as null; do not substitute another month without labeling a separate method.

Quarterly sensitivity analysis should sample March, June, September, and December as separate 12-month-ending snapshots. A rolling approach can average these reported monthly snapshots to describe smoothed burden, but cannot represent annual deaths. Never sum overlapping windows. These sensitivity outputs are implemented in `notebooks/02_sensitivity.py`; see `docs/sensitivity.md` for strict-window rules and cohort comparisons. Databricks execution of that notebook remains a separate deployment step. Compare them using consistent county coverage and report how suppression affects coverage.

## Interpretation

County associations are ecological and do not establish individual risk or causation. Legally dispensed opioids must not be described as causing all-drug overdose deaths; mortality includes drugs obtained through legal and illegal channels. Counts depend strongly on population size. With no additional population dataset, scatter plots are exploratory and cannot establish differences in mortality risk. No population data is introduced in this increment.

Provisional mortality values may be revised or incomplete. Freeze and document source releases. Retain only the reported series; predicted values, if supplied by CDC, require a distinct column and explicit labeling. No imputation or estimation is performed here. Complete-case analysis can systematically exclude small counties with suppressed counts. Display missingness alongside substantive charts.

## Verified mappings and remaining source questions

Uploaded-file column mappings, numeric months, FIPS normalization, suppression blanks, display bins, and name-alias pairs have been inspected; see `source_inspection.md`. Formal CDC source documentation is still needed to complete publication provenance and verify source definitions/units. The previous pandas implementation is needed to compare its month selection, release, and county-universe rules. Target counts alone cannot establish those choices.
