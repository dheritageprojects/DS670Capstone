# First Databricks AI/BI dashboard

Create a dashboard after the notebook passes its checks. Add a dataset with `SELECT * FROM <catalog>.<schema>.county_year` using your actual schema. Add year, state, and county FIPS filters to that dataset. FIPS is the initial county label until source names are confirmed. Do not label counts as death rates.

| View | Configuration |
|---|---|
| Dispensing trend | Year vs mean dispensing rate; show observed county count |
| Overdose trend | Year vs sum reported December counts; label as observed-county subtotal and display reporting coverage |
| Geographic comparison | State bar chart of mean dispensing and reported overdose subtotal; county comparison table |
| Association | Scatter: dispensing rate vs reported overdose count, one county-year per point; complete cases only |
| Missingness | Year/state vs missing dispensing and missing overdose counts, with total county-years |
| County details | Year, state, FIPS, both measures, and missingness flags |

Unweighted mean county dispensing rates are not statewide or national dispensing rates. Overdose subtotals exclude missing/suppressed counties and vary with coverage. Show coverage beside trends; do not present changes in these subtotals as changes in national totals. A county map requires confirmed geographic support; no boundary dataset has been added.

Before publishing, verify each filter changes all intended charts, nulls remain missing, tooltips show measure units, and sparse selections do not imply zero deaths. Dashboard creation and these acceptance checks remain pending Databricks authentication and real data.
