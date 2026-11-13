# Uploaded source inspection

## Dispensing: opioid_dispensing_2026_update.csv

SHA-256: `8cd88e062cab18e28d7ec7baa85f77c392c4e29665fb2cc35878c80023608f4d`

Computed using Python's CSV reader on the supplied file:

| Check | Observed |
|---|---:|
| Raw records, 2019–2024 | 18,864 |
| Distinct county FIPS | 3,144 |
| Records, 2020–2024 | 15,720 |
| Unavailable rates, 2020–2024 | 307 |
| Duplicate county-year keys, 2020–2024 | 0 |
| Invalid five-digit FIPS, 2020–2024 | 0 |

Mappings: `Location` → county FIPS, `Year` → year, `STATE_NAME` → state, `COUNTY_NAME` → county label, `Opioid Dispensing Rate` → numeric rate. The similarly named `Opioid Dispensing Rate (per 100 persons)` column contains display bins such as `< 17.7`, not individual numeric rates. Preserve `Data unavailable` as null.

The raw row count matches the prior target. The standalone analysis-period data have 10 more records and 10 more missing rates than the prior merged-data targets; this does not establish why the difference occurs. Check the overdose county universe and prior join rules before changing join semantics. Do not remove counties merely to reproduce a target.

## Overdose: overdose_deaths_2026_update.csv

Inspection blocked: the uploaded file exceeds the download tool's 32 MiB transfer limit. No rows, columns, or mortality results have been verified. Supply a compressed copy or direct download URL to continue.

No uploaded data are committed to Git. Original download URLs, release dates, and source definitions remain to be documented.
