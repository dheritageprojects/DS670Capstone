-- Read-only verification of saved quarter-end snapshots and every trailing calendar window.
WITH monthly AS (
 SELECT DISTINCT lpad(trim(FIPS),5,'0') AS county_fips, CAST(Year AS INT) AS year,
 CAST(Month AS INT) AS month,
 try_cast(replace(`Provisional Drug Overdose Deaths`,',','') AS DOUBLE) AS deaths
 FROM read_files('/Volumes/workspace/capstone/source_files/overdose.csv',format=>'csv',header=>true)
 WHERE CAST(Year AS INT) BETWEEN 2020 AND 2024
), windows AS (
 SELECT *, COUNT(*) OVER w AS required_rows, COUNT(deaths) OVER w AS observed,
 AVG(deaths) OVER w AS candidate
 FROM monthly WINDOW w AS (PARTITION BY county_fips ORDER BY year*12+month RANGE BETWEEN 2 PRECEDING AND CURRENT ROW)
), expected_rolling AS (
 SELECT *, CASE WHEN required_rows=3 AND observed=3 THEN candidate END AS strict_mean,true AS expected_present
 FROM windows
), expected_quarters AS (
 SELECT *,true AS expected_present FROM monthly WHERE month IN (3,6,9,12)
), actual_rolling AS (
 SELECT *,true AS actual_present FROM workspace.capstone.overdose_rolling3
), actual_quarters AS (
 SELECT *,true AS actual_present FROM workspace.capstone.overdose_quarterly
)
SELECT 'rolling_source_or_window_mismatches' AS check_name, COUNT(*) AS value
FROM expected_rolling e FULL OUTER JOIN actual_rolling a
ON e.county_fips=a.county_fips AND e.year=a.year AND e.month=a.month
WHERE e.expected_present IS NULL OR a.actual_present IS NULL
 OR NOT(e.deaths <=> a.overdose_count) OR NOT(e.required_rows <=> a.window_rows)
 OR NOT(e.observed <=> a.observed_months)
 OR (e.strict_mean IS NULL AND a.rolling_mean_3 IS NOT NULL)
 OR (e.strict_mean IS NOT NULL AND a.rolling_mean_3 IS NULL)
 OR ABS(e.strict_mean-a.rolling_mean_3)>1e-9
UNION ALL SELECT 'quarterly_source_mismatches',COUNT(*)
FROM expected_quarters e FULL OUTER JOIN actual_quarters a
ON e.county_fips=a.county_fips AND e.year=a.year AND e.month=a.month
WHERE e.expected_present IS NULL OR a.actual_present IS NULL OR NOT(e.deaths <=> a.overdose_count)
ORDER BY check_name
