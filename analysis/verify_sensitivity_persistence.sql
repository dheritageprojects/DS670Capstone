-- Read-only persistence checks against the independently validated live annual query.
WITH expected AS (
-- Read the existing source Volume; identical analytic aliases collapse before annualization.
WITH monthly AS (
  SELECT DISTINCT lpad(trim(FIPS), 5, '0') AS county_fips,
    CAST(Year AS INT) AS year, CAST(Month AS INT) AS month,
    try_cast(replace(`Provisional Drug Overdose Deaths`, ',', '') AS DOUBLE) AS deaths
  FROM read_files('/Volumes/workspace/capstone/source_files/overdose.csv', format => 'csv', header => true)
  WHERE CAST(Year AS INT) BETWEEN 2020 AND 2024
), annual AS (
  SELECT county_fips, year,
    MAX(CASE WHEN month = 12 THEN deaths END) AS december,
    CASE WHEN COUNT(CASE WHEN month IN (3,6,9,12) THEN deaths END) = 4
      THEN AVG(CASE WHEN month IN (3,6,9,12) THEN deaths END) END AS quarter_end_mean_4,
    CASE WHEN COUNT(deaths) = 12 THEN AVG(deaths) END AS monthly_mean_12,
    CASE WHEN COUNT(CASE WHEN month IN (10,11,12) THEN deaths END) = 3
      THEN AVG(CASE WHEN month IN (10,11,12) THEN deaths END) END AS december_trailing_mean_3
  FROM monthly GROUP BY county_fips, year
), methods AS (
  SELECT county_fips, year, december AS december_count,
    stack(4, 'december', december, 'quarter_end_mean_4', quarter_end_mean_4,
      'monthly_mean_12', monthly_mean_12, 'december_trailing_mean_3', december_trailing_mean_3)
      AS (method, overdose_measure)
  FROM annual
), joined AS (
  SELECT m.*, b.state, b.dispensing_rate,
    m.overdose_measure IS NOT NULL AND b.dispensing_rate IS NOT NULL AS complete_case
  FROM methods m INNER JOIN workspace.capstone.county_year_common b
    ON m.county_fips = b.county_fips AND m.year = b.year
)
-- Flags enable comparisons on identical cohorts; no counts from overlapping windows are summed.
SELECT *,
  SUM(CAST(complete_case AS INT)) OVER (PARTITION BY county_fips, year) = 4 AS common_within_year,
  SUM(CAST(complete_case AS INT)) OVER (PARTITION BY county_fips) = 20 AS common_all_years
FROM joined

), expected_annual AS (
 SELECT *, true AS expected_present FROM expected
), actual AS (
 SELECT *, true AS actual_present FROM workspace.capstone.sensitivity_county_year
), paired_annual AS (
 SELECT e.expected_present, a.actual_present, e.overdose_measure AS expected_measure,
  a.overdose_measure AS actual_measure, e.complete_case AS expected_complete, a.complete_case AS actual_complete
 FROM expected_annual e FULL OUTER JOIN actual a
 ON e.county_fips=a.county_fips AND e.year=a.year AND e.method=a.method
)
SELECT 'rows_overdose_quarterly' AS check_name, COUNT(*) AS value FROM workspace.capstone.overdose_quarterly
UNION ALL SELECT 'rows_overdose_rolling3',COUNT(*) FROM workspace.capstone.overdose_rolling3
UNION ALL SELECT 'rows_sensitivity_county_year',COUNT(*) FROM actual
UNION ALL SELECT 'rows_sensitivity_summary',COUNT(*) FROM workspace.capstone.sensitivity_summary
UNION ALL SELECT 'rows_sensitivity_paired',COUNT(*) FROM workspace.capstone.sensitivity_paired
UNION ALL SELECT 'annual_key_or_value_mismatches',COUNT(*) FROM paired_annual
 WHERE expected_present IS NULL OR actual_present IS NULL
 OR NOT(expected_complete <=> actual_complete)
 OR (expected_measure IS NULL AND actual_measure IS NOT NULL)
 OR (expected_measure IS NOT NULL AND actual_measure IS NULL)
 OR ABS(expected_measure-actual_measure)>1e-9
UNION ALL SELECT 'annual_duplicate_keys',COUNT(*) FROM (
 SELECT county_fips,year,method FROM actual GROUP BY county_fips,year,method HAVING COUNT(*)>1)
UNION ALL SELECT 'quarterly_duplicate_keys',COUNT(*) FROM (
 SELECT county_fips,year,month FROM workspace.capstone.overdose_quarterly GROUP BY county_fips,year,month HAVING COUNT(*)>1)
UNION ALL SELECT 'rolling_duplicate_keys',COUNT(*) FROM (
 SELECT county_fips,year,month FROM workspace.capstone.overdose_rolling3 GROUP BY county_fips,year,month HAVING COUNT(*)>1)
UNION ALL SELECT 'summary_duplicate_keys',COUNT(*) FROM (
 SELECT year,method,cohort FROM workspace.capstone.sensitivity_summary GROUP BY year,method,cohort HAVING COUNT(*)>1)
UNION ALL SELECT 'paired_duplicate_keys',COUNT(*) FROM (
 SELECT year,method FROM workspace.capstone.sensitivity_paired GROUP BY year,method HAVING COUNT(*)>1)
UNION ALL SELECT 'annual_incomplete_window_nonnull',COUNT(*) FROM actual
 WHERE (observed_periods < required_periods OR source_rows <> required_periods) AND overdose_measure IS NOT NULL
UNION ALL SELECT 'unexpected_imputation_flag',COUNT(*) FROM actual WHERE is_imputed IS NULL OR is_imputed<>false
UNION ALL SELECT 'quarterly_invalid_month_or_quarter',COUNT(*) FROM workspace.capstone.overdose_quarterly
 WHERE month NOT IN (3,6,9,12) OR NOT(quarter <=> CAST(month/3 AS INT))
UNION ALL SELECT 'rolling_incomplete_window_nonnull',COUNT(*) FROM workspace.capstone.overdose_rolling3
 WHERE (window_rows<>3 OR observed_months<>3) AND rolling_mean_3 IS NOT NULL
UNION ALL SELECT 'rolling_initial_boundary_nonnull',COUNT(*) FROM workspace.capstone.overdose_rolling3
 WHERE year=2020 AND month IN (1,2) AND rolling_mean_3 IS NOT NULL
ORDER BY check_name
