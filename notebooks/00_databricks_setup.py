# Databricks notebook source
# MAGIC %md
# MAGIC # First Databricks run
# MAGIC Run all on Databricks Python serverless compute. Creates `workspace.capstone` and a managed `source_files` Volume, downloads the supplied public CDC snapshots from a pinned GitHub revision, then executes the tested pipeline. Re-running overwrites the three project output tables. No token or additional Python package is required.

# COMMAND ----------
# Pin source and pipeline artifacts so this setup cannot silently follow changes to main.
import hashlib
import io
from pathlib import Path
from types import SimpleNamespace
import urllib.request
import zipfile

REVISION = 'e6f95284cf1b435302de029b9a47c6cf46872bff'
BASE = f'https://raw.githubusercontent.com/dheritageprojects/DS670Capstone/{REVISION}/'
HASHES = {
    'sources/dispensing.csv.zip': '318321ffbd7bd94d3267e78194e8213674f3c98601c86e427346f2c9a5249e37',
    'sources/overdose.csv.zip': 'c0b8ffa29fa39ab74ba0d4caa3b5ebc0b4a58b48e22fe9e95b611ccc1d4e1a1b',
    'notebooks/01_pipeline.py': '87dc159683733c57ff3014be3ec3b8a0e9f45310d0968dc80298e8fd29e5d733',
}

def verified_download(relative):
    with urllib.request.urlopen(BASE + relative, timeout=120) as response:
        content = response.read()
    assert hashlib.sha256(content).hexdigest() == HASHES[relative], f'Checksum mismatch: {relative}'
    return content

# COMMAND ----------
# Create the project storage location using the notebook user's existing permissions.
spark.sql('CREATE SCHEMA IF NOT EXISTS workspace.capstone')
spark.sql('CREATE VOLUME IF NOT EXISTS workspace.capstone.source_files')
volume = Path('/Volumes/workspace/capstone/source_files')
inputs = {}
for source in ('dispensing', 'overdose'):
    with zipfile.ZipFile(io.BytesIO(verified_download(f'sources/{source}.csv.zip'))) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith('.csv')]
        assert len(members) == 1, 'Expected one CSV per archive.'
        destination = volume / f'{source}.csv'
        destination.write_bytes(archive.read(members[0]))
        inputs[source] = str(destination)
print('Verified source files saved to', volume)

# COMMAND ----------
# Execute the checksum-verified pipeline with explicit settings and Delta persistence.
# The widget adapter supplies configuration without changing this notebook's UI widgets.
values = {
    'dispensing_path': inputs['dispensing'], 'overdose_path': inputs['overdose'],
    'output_schema': 'workspace.capstone', 'output_format': 'delta',
    'confirmed_single_reported_series': 'true',
}

class ConfigWidgets:
    def text(self, name, default):
        values.setdefault(name, default)

    def get(self, name):
        return values[name]

pipeline_code = verified_download('notebooks/01_pipeline.py').decode('utf-8')
exec(compile(pipeline_code, '01_pipeline.py', 'exec'), {
    'spark': spark, 'display': display,
    'dbutils': SimpleNamespace(widgets=ConfigWidgets()),
})

# COMMAND ----------
# Read back persisted Delta tables; show the quality report before dashboard creation.
display(spark.sql('SELECT * FROM workspace.capstone.quality_report ORDER BY metric'))
display(spark.sql('SELECT year, COUNT(*) AS county_years, SUM(CAST(complete_case AS INT)) AS complete_cases FROM workspace.capstone.county_year_common GROUP BY year ORDER BY year'))
print('Setup complete. Tables: workspace.capstone.county_year, county_year_common, quality_report.')
