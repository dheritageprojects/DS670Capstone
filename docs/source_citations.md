# Verified CDC sources and citation notes

Source pages supplied by the user and checked November 13, 2026. Tracking parameters have been removed. These verify publication identity and definitions; they do not establish the original uploaded files' download dates or exact release versions.

## Dispensing

Centers for Disease Control and Prevention. (2026, August 11). *Opioid dispensing rate maps*. National Center for Injury Prevention and Control. https://www.cdc.gov/overdose-prevention/data-research/facts-stats/opioid-dispensing-rate-maps.html

The page identifies IQVIA Xponent 2019–2024 as the dispensing source. Rates use projected annual opioid prescription totals and Census resident-population denominators, per 100 persons. They are source-estimated rates, not direct census counts of all prescriptions. The project uses them as supplied and adds no dispensing imputation.

Geography is based on **prescriber location**. The retail sample covers approximately 54,600 non-hospital pharmacies and nearly 94% of retail prescriptions; mail-order prescriptions and methadone dispensed through treatment programs are excluded. County maps cover approximately 98% of counties per year. The page's official statewide/national rates must not be substituted for this project's unweighted county means or described as equivalent to them.

## Overdose

National Center for Health Statistics. (n.d.). *VSRR provisional county-level drug overdose death counts* [Data set; Socrata ID gb4e-yj24]. Centers for Disease Control and Prevention. Retrieved November 13, 2026, from https://data.cdc.gov/National-Center-for-Health-Statistics/VSRR-Provisional-County-Level-Drug-Overdose-Death-/gb4e-yj24/about_data

DOI identified in publisher metadata: https://doi.org/10.15620/cdc/20250305009

The current metadata's suggested citation names Ahmad FB, Anderson RN, Cisewski JA, Rossen LM, and Sutton P, with a `[year]` placeholder. The organizational, undated citation above avoids guessing the uploaded release's citation year. Use the institution's required style and resolve the release year before final submission. The description also contains an older suggested citation; it should not be conflated with the current custom metadata.

Reported counts cover overlapping 12-month-ending periods, classified by decedent county of residence. June 2020, for example, includes July 2019 through June 2020. Counts 1–9 are suppressed. Underlying-cause ICD-10 codes are X40–X44, X60–X64, X85, and Y10–Y14; these identify all-drug overdoses, not deaths attributable exclusively to prescription opioids. Provisional completeness varies across jurisdictions and periods, and cause-of-death investigations can delay reporting.

## Cross-source alignment and release limitations

Matching five-digit FIPS aligns geographic identifiers but does not align the geographic attribution: prescriber location for dispensing differs from decedent residence for mortality. Dispensing also counts prescriptions, not people or exposure to illicit drugs. This limits interpretation of county associations even when all values are present.

The live mortality portal metadata extends beyond the supplied file's 2020–2025 years. Its update timestamp must not be assigned to the uploaded file, whose `Data as of` field is `07/05/2026`. The source page update date for dispensing is likewise not proof of the upload's exact release. No files or computed results have been replaced. Frozen source archive and CSV hashes remain the reproduction anchors.

Still unknown: exact original export URLs/queries, original download dates, and release identifiers connecting each uploaded file to a specific publication snapshot. The prior pandas source/code is also still needed to explain the historical target differences. Machine-readable definitions and provenance are in `sources/source_documentation.json` and `sources/manifest.json`.
