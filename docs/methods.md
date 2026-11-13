# Methods and limitations

## Annual alignment

The first dashboard uses December observations of reported 12-month-ending overdose deaths, aligned to annual dispensing for 2020–2024. December values can be missing or suppressed. Preserve them as null; do not substitute another month without labeling a separate method.

Quarterly sensitivity analysis should sample March, June, September, and December as separate 12-month-ending snapshots. A rolling approach can average these reported monthly snapshots to describe smoothed burden, but cannot represent annual deaths. Never sum overlapping windows. These sensitivity outputs are implemented in `notebooks/02_sensitivity.py`; see `docs/sensitivity.md` for strict-window rules and cohort comparisons. Databricks execution of that notebook remains a separate deployment step. Compare them using consistent county coverage and report how suppression affects coverage.

## Interpretation

County associations are ecological and do not establish individual risk or causation. Legally dispensed opioids must not be described as causing all-drug overdose deaths; mortality includes drugs obtained through legal and illegal channels. Counts depend strongly on population size. With no additional population dataset, scatter plots are exploratory and cannot establish differences in mortality risk. No population data is introduced in this increment.

Provisional mortality values may be revised or incomplete. Freeze and document source releases. Retain only the reported series; predicted values, if supplied by CDC, require a distinct column and explicit labeling. The project performs no analyst imputation or mortality prediction. The CDC dispensing rates are source estimates based on projected prescription totals; they must not be described as a complete observed prescription census. Complete-case analysis can systematically exclude small counties with suppressed counts. Display missingness alongside substantive charts.

## Verified mappings and remaining source questions

Uploaded-file column mappings, numeric months, FIPS normalization, suppression blanks, display bins, and name-alias pairs have been inspected; see `source_inspection.md`. CDC publication identity, source units, suppression definitions, and geographic attribution are now verified; see `source_citations.md`. Exact export/download and uploaded-release provenance remain incomplete. The previous pandas implementation is needed to compare its month selection, release, and county-universe rules. Target counts alone cannot establish those choices.

## Verified geographic attribution limitation

CDC dispensing geography follows prescriber location; provisional deaths follow decedent county of residence. Matching FIPS aligns identifiers, not identical exposure/residence definitions. The dispensing retail sample excludes mail-order prescriptions and methadone dispensed through treatment programs. This limits county association interpretation and is documented in the report.
