"""Check source CSVs locally without Spark; usage: python tests/check_uploaded_sources.py dispensing.csv overdose.zip."""

# Read original CSVs without converting suppressed values to zero.
import csv
import io
import sys
import zipfile
from collections import defaultdict

with open(sys.argv[1], encoding='utf-8-sig', newline='') as stream:
    dispensing = list(csv.DictReader(stream))
with zipfile.ZipFile(sys.argv[2]) as archive:
    members = [n for n in archive.namelist() if n.lower().endswith('.csv')]
    assert len(members) == 1, 'Expected exactly one CSV.'
    with archive.open(members[0]) as stream:
        overdose = list(csv.DictReader(io.TextIOWrapper(stream, encoding='utf-8-sig')))

# Verify that duplicate source keys differ only by county alias, not measurements.
groups = defaultdict(list)
for row in overdose:
    groups[(row['FIPS'].zfill(5), row['Year'], row['Month'])].append(row)
for group in groups.values():
    assert len({tuple(sorted((k, v) for k, v in row.items() if k != 'COUNTYNAME')) for row in group}) == 1, 'Conflicting overdose records.'

# Align December snapshots with annual dispensing on shared county-year keys.
d = {(r['Location'], r['Year']): r for r in dispensing if '2020' <= r['Year'] <= '2024'}
assert len(d) == sum('2020' <= r['Year'] <= '2024' for r in dispensing), 'Duplicate dispensing keys.'
o = {(fips, year): group[0] for (fips, year, month), group in groups.items() if month == '12' and '2020' <= year <= '2024'}
keys = d.keys() & o.keys()
complete = [k for k in keys if d[k]['Opioid Dispensing Rate'] != 'Data unavailable' and o[k]['Provisional Drug Overdose Deaths'] != '']

# Report actual observations beside historical targets; differences are evidence, not failures to hide.
actual = [len(dispensing), len(overdose), len({k[0] for k in keys}), len(keys), len(complete), len({k[0] for k in complete}), sum(d[k]['Opioid Dispensing Rate'] == 'Data unavailable' for k in keys), sum(o[k]['Provisional Drug Overdose Deaths'] == '' for k in keys)]
targets = [('raw_dispensing', 18864), ('raw_overdose', 226368), ('matching_fips', 3142), ('merged_county_years', 15710), ('complete_observations', 8180), ('complete_counties', 2385), ('missing_dispensing', 297), ('missing_overdose', 7298)]
for (metric, target), value in zip(targets, actual):
    print(f'{metric}: actual={value}, target={target}, difference={value-target:+d}')
