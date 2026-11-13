"""Independent standard-library reference for annual correlations and cohort trends."""
# Rank ties at their average position so Spearman matches the SQL window expression.
import csv
import io
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path

def average_ranks(values):
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        for position in range(start, end):
            result[ordered[position][0]] = (start + 1 + end) / 2
        start = end
    return result

def correlation(x, y):
    if len(x) < 2 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    return statistics.correlation(x, y)

# Read the supplied snapshots directly; retain suppression as None and literal zero as zero.
def read_source(root, name):
    with zipfile.ZipFile(Path(root) / 'sources' / f'{name}.csv.zip') as archive:
        member = next(n for n in archive.namelist() if n.endswith('.csv'))
        with archive.open(member) as stream:
            yield from csv.DictReader(io.TextIOWrapper(stream, encoding='utf-8-sig'))

def summaries(root):
    dispensing = {}
    for row in read_source(root, 'dispensing'):
        if 2020 <= int(row['Year']) <= 2024:
            token = row['Opioid Dispensing Rate']
            dispensing[(row['Location'], int(row['Year']))] = None if token == 'Data unavailable' else float(token)
    monthly = defaultdict(dict)
    for row in read_source(root, 'overdose'):
        if 2020 <= int(row['Year']) <= 2024:
            key = row['FIPS'].zfill(5), int(row['Year'])
            month = int(row['Month'])
            token = row['Provisional Drug Overdose Deaths'].replace(',', '')
            value = float(token) if token else None
            assert month not in monthly[key] or monthly[key][month] == value
            monthly[key][month] = value
    windows = {'december': [12], 'quarter_end_mean_4': [3,6,9,12], 'monthly_mean_12': list(range(1,13)), 'december_trailing_mean_3': [10,11,12]}
    annual = {}
    for key in dispensing.keys() & monthly.keys():
        annual[key] = {}
        for method, months in windows.items():
            values = [monthly[key].get(m) for m in months]
            annual[key][method] = statistics.fmean(values) if all(v is not None for v in values) else None
    shared = {key for key, values in annual.items() if dispensing[key] is not None and all(v is not None for v in values.values())}
    fixed = {county for county, _ in shared if all((county, year) in shared for year in range(2020,2025))}

    # Calculate year-specific associations; do not pool repeated county observations across years.
    groups = defaultdict(list)
    for key, methods in annual.items():
        county, year = key
        for method, value in methods.items():
            if dispensing[key] is None or value is None:
                continue
            groups[('available', method, year)].append((dispensing[key], value))
            if key in shared:
                groups[('common_within_year', method, year)].append((dispensing[key], value))
            if county in fixed:
                groups[('common_all_years', method, year)].append((dispensing[key], value))
    result = []
    baselines = {}
    for (cohort, method, year), pairs in sorted(groups.items()):
        x, y = map(list, zip(*pairs))
        dx, dy = statistics.fmean(x), statistics.fmean(y)
        if year == 2020:
            baselines[(cohort, method)] = dx, dy
        bx, by = baselines[(cohort, method)]
        result.append(dict(cohort=cohort,year=year,method=method,complete_counties=len(pairs),mean_county_dispensing=dx,mean_county_overdose_measure=dy,pearson_r=correlation(x,y),spearman_rho=correlation(average_ranks(x),average_ranks(y)),dispensing_2020=bx,overdose_2020=by,dispensing_pct_change_since_2020=100*(dx-bx)/bx if bx else None,overdose_pct_change_since_2020=100*(dy-by)/by if by else None))
    return result

# Independently reproduce state coverage and county means on the common county universe.
def geographic_summaries(root):
    dispensing = {}
    for row in read_source(root, 'dispensing'):
        if 2020 <= int(row['Year']) <= 2024:
            token = row['Opioid Dispensing Rate']
            dispensing[(row['Location'], int(row['Year']))] = (row['STATE_NAME'], None if token == 'Data unavailable' else float(token))
    overdose = {}
    for row in read_source(root, 'overdose'):
        if row['Month'] == '12' and 2020 <= int(row['Year']) <= 2024:
            key = row['FIPS'].zfill(5), int(row['Year'])
            token = row['Provisional Drug Overdose Deaths'].replace(',', '')
            value = float(token) if token else None
            assert key not in overdose or overdose[key] == value
            overdose[key] = value
    groups = defaultdict(list)
    for key in dispensing.keys() & overdose.keys():
        state, value = dispensing[key]
        groups[(state,key[1])].append((value,overdose[key]))
    rows=[]
    for (state,year), pairs in sorted(groups.items()):
        d = [x for x,y in pairs if x is not None]
        o = [y for x,y in pairs if y is not None]
        rows.append(dict(state=state,year=year,eligible_counties=len(pairs),dispensing_reported_counties=len(d),overdose_reported_counties=len(o),complete_counties=sum(x is not None and y is not None for x,y in pairs),mean_county_dispensing=statistics.fmean(d) if d else None,mean_reported_county_overdose=statistics.fmean(o) if o else None,observed_overdose_subtotal=sum(o) if o else None,missing_overdose_pct=100*(len(pairs)-len(o))/len(pairs)))
    return rows
