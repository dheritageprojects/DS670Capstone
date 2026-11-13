"""Independent CSV reference calculations for strict smoothing and Spark agreement."""
# Compute expected annual means directly from source values without Spark functions.
import csv
from collections import defaultdict
from pathlib import Path
import math

def check_sensitivity(spark, overdose_path, dispensing_path, schema):
    groups = defaultdict(dict)
    with open(overdose_path, encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            if not 2020 <= int(row['Year']) <= 2024:
                continue
            key = (row['FIPS'].zfill(5), int(row['Year']))
            month = int(row['Month'])
            value = float(row['Provisional Drug Overdose Deaths'].replace(',', '')) if row['Provisional Drug Overdose Deaths'] else None
            if month in groups[key]:
                assert groups[key][month] == value, 'Conflicting source aliases.'
            groups[key][month] = value
    with open(dispensing_path, encoding='utf-8-sig', newline='') as stream:
        dispensing = {(r['Location'], int(r['Year'])) for r in csv.DictReader(stream) if 2020 <= int(r['Year']) <= 2024}
    windows = {'december': [12], 'quarter_end_mean_4': [3,6,9,12], 'monthly_mean_12': list(range(1,13)), 'december_trailing_mean_3': [10,11,12]}
    expected = {}
    for key in groups.keys() & dispensing:
        for method, months in windows.items():
            values = [groups[key].get(m) for m in months]
            expected[(*key, method)] = sum(values)/len(values) if all(v is not None for v in values) else None

    # Compare every county-year-method, including nulls; do not assert historical target counts.
    actual = spark.table(f'{schema}.sensitivity_county_year').select('county_fips','year','method','overdose_measure').collect()
    assert len(actual) == len(expected)
    for row in actual:
        value = expected[(row.county_fips, row.year, row.method)]
        if value is None:
            assert row.overdose_measure is None
        else:
            assert math.isclose(row.overdose_measure, value, rel_tol=1e-12, abs_tol=1e-10)

    # Check the live dashboard SQL implementation against the same independent reference.
    spark.read.option('header', True).csv(overdose_path).createOrReplaceTempView('sensitivity_source')
    sql = (Path(__file__).resolve().parents[1] / 'dashboard/sensitivity_dataset.sql').read_text()
    sql = sql.replace("read_files('/Volumes/workspace/capstone/source_files/overdose.csv', format => 'csv', header => true)", 'sensitivity_source').replace('workspace.capstone.county_year_common', f'{schema}.county_year_common')
    sql_rows = spark.sql(sql).select('county_fips','year','method','overdose_measure').collect()
    assert len(sql_rows) == len(expected)
    for row in sql_rows:
        value = expected[(row.county_fips, row.year, row.method)]
        assert (row.overdose_measure is None) if value is None else math.isclose(row.overdose_measure, value, rel_tol=1e-12, abs_tol=1e-10)

    # Verify calendar-boundary rolling windows and preservation of missingness and reported zero.
    rolling = spark.table(f'{schema}.overdose_rolling3')
    assert rolling.filter('year = 2020 AND month IN (1,2) AND rolling_mean_3 IS NOT NULL').count() == 0
    for row in rolling.filter('month = 1 AND year = 2021').select('county_fips','rolling_mean_3').collect():
        values = [groups[(row.county_fips, 2020)][11], groups[(row.county_fips, 2020)][12], groups[(row.county_fips, 2021)][1]]
        expected_value = sum(values)/3 if all(v is not None for v in values) else None
        assert (row.rolling_mean_3 is None) if expected_value is None else math.isclose(row.rolling_mean_3, expected_value, rel_tol=1e-12, abs_tol=1e-10)
    assert rolling.filter('observed_months < 3 AND rolling_mean_3 IS NOT NULL').count() == 0
    assert any(v == 0 for v in expected.values()), 'Reference contains reported zero measures.'
    print('PASS: every strict annual mean matches independent CSV reference; suppression and calendar windows preserved.')
