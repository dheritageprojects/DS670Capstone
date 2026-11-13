-- State summaries use county means and observed-count subtotals, never state mortality rates.
SELECT state, year, COUNT(*) AS eligible_counties,
 COUNT(dispensing_rate) AS dispensing_reported_counties,
 COUNT(overdose_count) AS overdose_reported_counties,
 SUM(CAST(complete_case AS INT)) AS complete_counties,
 AVG(dispensing_rate) AS mean_county_dispensing,
 AVG(overdose_count) AS mean_reported_county_overdose,
 SUM(overdose_count) AS observed_overdose_subtotal,
 100.0 * SUM(CAST(missing_overdose AS INT)) / COUNT(*) AS missing_overdose_pct
FROM workspace.capstone.county_year_common
GROUP BY state, year ORDER BY state, year
