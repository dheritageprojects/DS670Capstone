# Databricks notebook source
# MAGIC %md
# MAGIC # County dispensing and overdose pipeline
# MAGIC Configure exact source columns after inspecting CDC metadata. Use only one reported all-drug county series. No estimates or imputations are produced.

# COMMAND ----------
# Configure source paths, column mappings, and a writable output schema.
import re
from pyspark.sql import functions as F

defaults = {
    'dispensing_path': '', 'overdose_path': '', 'output_schema': '',
    'dispensing_fips': 'Location', 'dispensing_year': 'Year', 'dispensing_rate': 'Opioid Dispensing Rate',
    'overdose_fips': '', 'overdose_year': '', 'overdose_month': '',
    'overdose_count': '', 'dispensing_state': 'STATE_NAME',
    'confirmed_single_reported_series': 'false',
}
for name, default in defaults.items():
    dbutils.widgets.text(name, default)
cfg = {name: dbutils.widgets.get(name).strip() for name in defaults}
assert all(cfg.values()), 'Populate every widget from confirmed source metadata.'
assert cfg['confirmed_single_reported_series'].lower() == 'true', 'Confirm a single reported overdose series first.'
assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*', cfg['output_schema']), 'Use catalog.schema.'
schema = cfg['output_schema']

# COMMAND ----------
# Read original CSV values as strings to preserve suppression markers and FIPS.
disp_raw = spark.read.option('header', True).csv(cfg['dispensing_path'])
over_raw = spark.read.option('header', True).csv(cfg['overdose_path'])
for frame, names in [(disp_raw, ['dispensing_fips', 'dispensing_year', 'dispensing_rate', 'dispensing_state']),
                     (over_raw, ['overdose_fips', 'overdose_year', 'overdose_month', 'overdose_count'])]:
    assert set(cfg[n] for n in names) <= set(frame.columns), 'A mapped column is absent.'

# COMMAND ----------
# Parse values conservatively; expand missing tokens only after reviewing CDC metadata.
MISSING = ['', 'suppressed', 'missing', 'data unavailable', 'na', 'n/a', 'null', '*', '**', '--']
def source_col(name):
    return F.col('`' + cfg[name].replace('`', '``') + '`')

def fips(column):
    value = F.trim(column)
    return F.when(value.rlike(r'^\d{1,5}$'), F.lpad(value, 5, '0'))

def number(column):
    value = F.trim(column)
    clean = F.regexp_replace(value, ',', '')
    return F.when(~F.lower(value).isin(MISSING) & clean.rlike(r'^\d+(\.\d+)?$'), clean.cast('double'))

def assert_empty(frame, message):
    assert frame.limit(1).count() == 0, message

disp = disp_raw.select(
    fips(source_col('dispensing_fips')).alias('county_fips'),
    source_col('dispensing_year').alias('year_raw'),
    source_col('dispensing_state').alias('state'),
    source_col('dispensing_rate').alias('value_raw'),
).withColumn('year', F.expr('try_cast(year_raw as int)')).withColumn('dispensing_rate', number(F.col('value_raw')))
over = over_raw.select(
    fips(source_col('overdose_fips')).alias('county_fips'),
    source_col('overdose_year').alias('year_raw'),
    source_col('overdose_month').alias('month_raw'),
    source_col('overdose_count').alias('value_raw'),
).withColumn('year', F.expr('try_cast(year_raw as int)')).withColumn('month', F.expr('try_cast(month_raw as int)')).withColumn('overdose_count', number(F.col('value_raw')))

# COMMAND ----------
# Reject malformed keys and unrecognized numeric tokens before filtering or joining.
for frame, measure in [(disp, 'dispensing_rate'), (over, 'overdose_count')]:
    assert_empty(frame.filter(F.col('county_fips').isNull() | F.col('year').isNull()), 'Invalid FIPS/year: inspect source mapping.')
    unknown = F.col('value_raw').isNotNull() & ~F.lower(F.trim(F.col('value_raw'))).isin(MISSING) & F.col(measure).isNull()
    assert_empty(frame.filter(unknown), 'Unrecognized value token: review metadata, never coerce blindly.')
assert_empty(over.filter(F.col('month').isNull() | ~F.col('month').between(1, 12)), 'Months must be numeric 1–12; adapt mapping explicitly if needed.')
disp = disp.filter(F.col('year').between(2020, 2024))
over = over.filter(F.col('year').between(2020, 2024))
for frame, keys in [(disp, ['county_fips', 'year']), (over, ['county_fips', 'year', 'month'])]:
    assert_empty(frame.groupBy(*keys).count().filter('count > 1'), 'Duplicate county-period keys: resolve series dimensions before proceeding.')

# COMMAND ----------
# Use December 12-month-ending counts as annual observations; never sum monthly windows.
annual = over.filter('month = 12').select('county_fips', 'year', 'overdose_count')
states = disp.select('county_fips', 'state').distinct()
assert_empty(states.groupBy('county_fips').count().filter('count > 1'), 'Inconsistent state labels for county.')
panel = disp.select('county_fips', 'year', 'dispensing_rate').join(annual, ['county_fips', 'year'], 'full').join(states, 'county_fips', 'left')
panel = panel.withColumn('state_fips', F.substring('county_fips', 1, 2)).withColumn('state', F.coalesce('state', 'state_fips'))
panel = panel.withColumn('missing_dispensing', F.col('dispensing_rate').isNull()).withColumn('missing_overdose', F.col('overdose_count').isNull())
panel = panel.withColumn('complete_case', ~F.col('missing_dispensing') & ~F.col('missing_overdose')).withColumn('overdose_method', F.lit('reported_december_12_month_ending'))
assert_empty(panel.groupBy('county_fips', 'year').count().filter('count > 1'), 'Integrated keys are not unique.')

# COMMAND ----------
# Compare computed metrics against prior pandas targets without changing observations.
complete = panel.filter('complete_case')
matching = disp.select('county_fips').distinct().join(over.select('county_fips').distinct(), 'county_fips', 'inner').count()
actual = [disp_raw.count(), over_raw.count(), matching, panel.count(), complete.count(), complete.select('county_fips').distinct().count(), panel.filter('missing_dispensing').count(), panel.filter('missing_overdose').count()]
targets = [('raw_dispensing', 18864), ('raw_overdose', 226368), ('matching_fips', 3142), ('merged_county_years', 15710), ('complete_observations', 8180), ('complete_counties', 2385), ('missing_dispensing', 297), ('missing_overdose', 7298)]
quality = spark.createDataFrame([(name, value, target, value - target) for (name, target), value in zip(targets, actual)], 'metric string, actual long, target long, difference long')
display(quality)

# COMMAND ----------
# Persist dashboard tables only after blocking checks pass; target differences remain visible.
spark.sql(f'CREATE SCHEMA IF NOT EXISTS {schema}')
panel.write.format('delta').mode('overwrite').saveAsTable(f'{schema}.county_year')
quality.withColumn('run_timestamp', F.current_timestamp()).write.format('delta').mode('overwrite').saveAsTable(f'{schema}.quality_report')
display(panel.groupBy('year').agg(F.count('*').alias('county_years'), F.sum(F.col('complete_case').cast('int')).alias('complete_cases')).orderBy('year'))
