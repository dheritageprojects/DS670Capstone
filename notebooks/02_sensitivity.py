# Databricks notebook source
# MAGIC %md
# MAGIC # Annualization sensitivity: reported snapshots and strict smoothing
# MAGIC Compare December with quarter-end and monthly snapshot means. Smoothed values are derived measures of reported burden, not estimated annual deaths. Any missing constituent makes a strict mean null. No imputation or summing overlapping windows.

# COMMAND ----------
# Configure existing source storage and a separate set of sensitivity output tables.
import re
from pyspark.sql import functions as F
from pyspark.sql import Window

settings = {
    'overdose_path': '/Volumes/workspace/capstone/source_files/overdose.csv',
    'output_schema': 'workspace.capstone', 'output_format': 'delta',
}
for name, value in settings.items():
    dbutils.widgets.text(name, value)
cfg = {name: dbutils.widgets.get(name).strip() for name in settings}
assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*', cfg['output_schema'])
assert cfg['output_format'] in ('delta', 'parquet')
schema = cfg['output_schema']

# COMMAND ----------
# Preserve raw strings and validate the known CDC schema before normalizing monthly observations.
raw = spark.read.option('header', True).csv(cfg['overdose_path'])
required = {'FIPS', 'Year', 'Month', 'Provisional Drug Overdose Deaths', 'COUNTYNAME'}
assert required <= set(raw.columns), 'Unexpected source schema.'
missing_tokens = ['', 'suppressed', 'missing', 'data unavailable', 'na', 'n/a', 'null', '*', '**', '--']
monthly = raw.select(
    F.trim('FIPS').alias('fips_raw'), F.col('Year').alias('year_raw'),
    F.col('Month').alias('month_raw'), F.col('Provisional Drug Overdose Deaths').alias('count_raw'),
).withColumn('county_fips', F.when(F.col('fips_raw').rlike(r'^\d{1,5}$'), F.lpad('fips_raw', 5, '0')))
monthly = monthly.withColumn('year', F.expr('try_cast(year_raw as int)')).withColumn('month', F.expr('try_cast(month_raw as int)'))
value = F.regexp_replace(F.trim('count_raw'), ',', '')
monthly = monthly.withColumn('overdose_count', F.when(value.rlike(r'^\d+$'), value.cast('double')))

def empty(frame, message):
    assert frame.limit(1).count() == 0, message

empty(monthly.filter(F.col('county_fips').isNull() | F.col('year').isNull() | F.col('month').isNull() | ~F.col('month').between(1, 12)), 'Invalid source keys.')
empty(monthly.filter(F.col('count_raw').isNotNull() & ~F.lower(F.trim('count_raw')).isin(missing_tokens) & F.col('overdose_count').isNull()), 'Unrecognized count token.')
# Collapse only identical selected source values; conflicting counts fail the unique-key check.
monthly = monthly.dropDuplicates().filter(F.col('year').between(2020, 2024))
empty(monthly.groupBy('county_fips', 'year', 'month').count().filter('count > 1'), 'Conflicting monthly observations.')
monthly = monthly.select('county_fips', 'year', 'month', 'overdose_count').cache()

# COMMAND ----------
# Retain quarter-end 12-month-ending observations as distinct snapshots, never quarterly death totals.
quarterly = monthly.filter(F.col('month').isin(3, 6, 9, 12)).withColumn('quarter', (F.col('month') / 3).cast('int'))
quarterly = quarterly.withColumn('measure_kind', F.lit('reported_12_month_ending_snapshot'))

# COMMAND ----------
# Compute trailing three-month snapshot means using a month index, including cross-year windows.
# Calendar range windows prevent a missing source month from being replaced by an older row.
indexed = monthly.withColumn('month_index', F.col('year') * 12 + F.col('month'))
window = Window.partitionBy('county_fips').orderBy('month_index').rangeBetween(-2, 0)
rolling = indexed.withColumn('window_rows', F.count('*').over(window)).withColumn('observed_months', F.count('overdose_count').over(window))
rolling = rolling.withColumn('rolling_mean_3', F.when((F.col('window_rows') == 3) & (F.col('observed_months') == 3), F.avg('overdose_count').over(window)))
rolling = rolling.withColumn('measure_kind', F.lit('derived_mean_of_reported_snapshots')).drop('month_index')

# COMMAND ----------
# Construct four explicitly labeled annual measures; strict smoothing needs every constituent reported.
keys = ['county_fips', 'year']
annual_parts = []

def annual_measure(frame, method, expected, kind):
    grouped = frame.groupBy(*keys).agg(F.count('*').alias('source_rows'), F.count('overdose_count').alias('observed_periods'), F.avg('overdose_count').alias('candidate'))
    return grouped.select(*keys, F.lit(method).alias('method'), F.lit(kind).alias('measure_kind'), F.lit(expected).alias('required_periods'), 'source_rows', 'observed_periods', F.when((F.col('source_rows') == expected) & (F.col('observed_periods') == expected), F.col('candidate')).alias('overdose_measure'))

annual_parts.append(annual_measure(monthly.filter('month = 12'), 'december', 1, 'reported_12_month_ending_count'))
annual_parts.append(annual_measure(quarterly, 'quarter_end_mean_4', 4, 'derived_mean_of_reported_snapshots'))
annual_parts.append(annual_measure(monthly, 'monthly_mean_12', 12, 'derived_mean_of_reported_snapshots'))
annual_parts.append(annual_measure(monthly.filter('month IN (10, 11, 12)'), 'december_trailing_mean_3', 3, 'derived_mean_of_reported_snapshots'))
annual = annual_parts[0]
for part in annual_parts[1:]:
    annual = annual.unionByName(part)
# Restrict comparisons to the same county-year universe used by the primary common-key analysis.
base = spark.table(f'{schema}.county_year_common').select('county_fips', 'year', 'state', 'dispensing_rate')
annual = annual.join(base, keys, 'inner').withColumn('complete_case', F.col('dispensing_rate').isNotNull() & F.col('overdose_measure').isNotNull())
annual = annual.withColumn('is_imputed', F.lit(False)).cache()
empty(annual.groupBy(*keys, 'method').count().filter('count > 1'), 'Duplicate sensitivity keys.')
empty(annual.filter('observed_periods < required_periods AND overdose_measure IS NOT NULL'), 'Incomplete window produced a strict mean.')

# COMMAND ----------
# Compare methods both on available data and on shared county cohorts to expose selection effects.
shared_keys = annual.groupBy(*keys).agg(F.sum(F.col('complete_case').cast('int')).alias('complete_methods')).filter('complete_methods = 4').select(*keys)
shared = annual.join(shared_keys, keys, 'inner')
fixed_counties = shared_keys.groupBy('county_fips').agg(F.countDistinct('year').alias('years')).filter('years = 5').select('county_fips')
fixed = shared.join(fixed_counties, 'county_fips', 'inner')

def summarize(frame, label):
    return frame.groupBy('year', 'method', 'measure_kind').agg(
        F.count('*').alias('eligible_county_years'),
        F.count('overdose_measure').alias('observed_overdose_county_years'),
        F.sum(F.col('complete_case').cast('int')).alias('complete_county_years'),
        F.avg('overdose_measure').alias('mean_county_overdose_measure'),
        F.avg(F.when(F.col('complete_case'), F.col('overdose_measure'))).alias('mean_overdose_complete_cases'),
        F.corr(F.when(F.col('complete_case'), F.col('dispensing_rate')), F.when(F.col('complete_case'), F.col('overdose_measure'))).alias('pearson_dispensing_vs_count'),
    ).withColumn('cohort', F.lit(label))

summary = summarize(annual, 'available').unionByName(summarize(shared, 'common_within_year')).unionByName(summarize(fixed, 'common_all_years'))
# Pair each alternate method with December on identical complete county-years.
december = annual.filter("method = 'december'").select(*keys, F.col('overdose_measure').alias('december_count'))
paired = annual.join(december, keys, 'inner').filter('complete_case AND december_count IS NOT NULL').groupBy('year', 'method').agg(F.count('*').alias('paired_counties'), F.avg(F.col('overdose_measure') - F.col('december_count')).alias('mean_difference_from_december'), F.avg(F.abs(F.col('overdose_measure') - F.col('december_count'))).alias('mean_absolute_difference_from_december'))

# COMMAND ----------
# Save separate sensitivity tables; leave the confirmed primary dashboard tables unchanged.
outputs = {'overdose_quarterly': quarterly, 'overdose_rolling3': rolling, 'sensitivity_county_year': annual, 'sensitivity_summary': summary, 'sensitivity_paired': paired}
for table, frame in outputs.items():
    frame.write.format(cfg['output_format']).mode('overwrite').saveAsTable(f'{schema}.{table}')
display(summary.orderBy('cohort', 'year', 'method'))
display(paired.orderBy('year', 'method'))
annual.unpersist()
monthly.unpersist()
