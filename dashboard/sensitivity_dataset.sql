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
