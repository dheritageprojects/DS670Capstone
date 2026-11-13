"""Execute the actual notebook on local Spark with Parquet table persistence."""

# Unpack the versioned public CDC snapshots into an isolated temporary directory.
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import zipfile

os.environ.setdefault('SPARK_LOCAL_IP', '127.0.0.1')
from pyspark.sql import SparkSession

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='capstone-') as temporary:
    work = Path(temporary)
    paths = {}
    for source in ('dispensing', 'overdose'):
        with zipfile.ZipFile(root / 'sources' / f'{source}.csv.zip') as archive:
            names = [n for n in archive.namelist() if n.endswith('.csv')]
            assert len(names) == 1
            destination = work / f'{source}.csv'
            destination.write_bytes(archive.read(names[0]))
            paths[source] = str(destination)

    # Run the independent source checker before executing notebook transformations.
    subprocess.run([sys.executable, str(root / 'tests/check_uploaded_sources.py'), paths['dispensing'], str(root / 'sources/overdose.csv.zip')], check=True)
    values = dict(dispensing_path=paths['dispensing'], overdose_path=paths['overdose'], output_schema='spark_catalog.capstone', confirmed_single_reported_series='true', output_format='parquet')

    # Emulate only Databricks widgets/display; run every Spark transformation unchanged.
    class Widgets:
        def text(self, name, default):
            values.setdefault(name, default)

        def get(self, name):
            return values[name]

    spark = (SparkSession.builder.master('local[2]').appName('capstone-ci')
             .config('spark.sql.warehouse.dir', str(work / 'warehouse'))
             .config('spark.sql.shuffle.partitions', '4')
             .config('spark.ui.enabled', 'false').getOrCreate())
    spark.sparkContext.setLogLevel('ERROR')
    try:
        scope = runpy.run_path(str(root / 'notebooks/01_pipeline.py'), init_globals={'spark': spark, 'dbutils': SimpleNamespace(widgets=Widgets()), 'display': lambda frame: frame.show(truncate=False)})

        # Verify persisted tables and null flags agree with the computed results.
        panel = spark.table('spark_catalog.capstone.county_year')
        common = spark.table('spark_catalog.capstone.county_year_common')
        assert common.count() == scope['comparison'].count()
        assert panel.count() == scope['panel'].count()
        assert panel.filter('missing_overdose != (overdose_count IS NULL)').count() == 0
        assert panel.filter('overdose_count = 0').count() > 0, 'Reported zeros must survive.'
        quality = spark.table('spark_catalog.capstone.quality_report')
        assert quality.count() == 8
        print('PASS: source checks, full notebook execution, and persisted-table checks.')
    finally:
        spark.stop()
