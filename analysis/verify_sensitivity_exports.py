"""Independently validate saved Delta-table verification exports from frozen CSV inputs."""
# Rebuild strict annual measures with standard-library arithmetic, not saved Spark expressions.
import json
import math
from collections import defaultdict
from pathlib import Path
import statistics
from analysis.reference import read_source,correlation

ROOT=Path(__file__).resolve().parents[1]

def expected_outputs(root=ROOT):
    d={}
    for row in read_source(root,'dispensing'):
        if 2020<=int(row['Year'])<=2024:
            token=row['Opioid Dispensing Rate']
            d[(row['Location'],int(row['Year']))]=None if token=='Data unavailable' else float(token)
    monthly=defaultdict(dict)
    for row in read_source(root,'overdose'):
        if 2020<=int(row['Year'])<=2024:
            key=(row['FIPS'].zfill(5),int(row['Year']));month=int(row['Month'])
            token=row['Provisional Drug Overdose Deaths'].replace(',','')
            value=float(token) if token else None
            assert month not in monthly[key] or monthly[key][month]==value
            monthly[key][month]=value
    windows={'december':[12],'quarter_end_mean_4':[3,6,9,12],'monthly_mean_12':list(range(1,13)),'december_trailing_mean_3':[10,11,12]}
    annual={}
    for key in d.keys()&monthly.keys():
        annual[key]={}
        for method,months in windows.items():
            values=[monthly[key].get(m) for m in months]
            annual[key][method]=statistics.fmean(values) if all(v is not None for v in values) else None
    shared={key for key,methods in annual.items() if d[key] is not None and all(v is not None for v in methods.values())}
    fixed={county for county,_ in shared if all((county,year) in shared for year in range(2020,2025))}
    groups=defaultdict(list);pairs=defaultdict(list)
    for key,methods in annual.items():
        county,year=key
        for method,value in methods.items():
            for cohort,include in [('available',True),('common_within_year',key in shared),('common_all_years',county in fixed)]:
                if include:groups[(cohort,method,year)].append((d[key],value))
            if d[key] is not None and value is not None and methods['december'] is not None:
                pairs[(method,year)].append(value-methods['december'])
    summaries={}
    for key,values in groups.items():
        observed=[y for x,y in values if y is not None];complete=[(x,y) for x,y in values if x is not None and y is not None]
        xs,ys=map(list,zip(*complete))
        summaries[key]={'eligible_county_years':len(values),'observed_overdose_county_years':len(observed),'complete_county_years':len(complete),'mean_county_overdose_measure':statistics.fmean(observed),'mean_overdose_complete_cases':statistics.fmean(ys),'pearson_dispensing_vs_count':correlation(xs,ys)}
    paired={key:{'paired_counties':len(v),'mean_difference_from_december':statistics.fmean(v),'mean_absolute_difference_from_december':statistics.fmean(abs(x) for x in v)} for key,v in pairs.items()}
    counts={'rows_overdose_quarterly':sum(m in (3,6,9,12) for months in monthly.values() for m in months),'rows_overdose_rolling3':sum(len(months) for months in monthly.values()),'rows_sensitivity_county_year':len(annual)*len(windows),'rows_sensitivity_summary':len(summaries),'rows_sensitivity_paired':len(paired)}
    return summaries,paired,counts

# Require complete result exports and compare numeric summaries within floating-point tolerance.
def load_rows(name,root):
    result=json.loads((Path(root)/'analysis'/f'sensitivity_{name}_verification.json').read_text())
    assert not result['truncated'] and len(result['rows'])==result['total_row_count']
    columns=[c['name'] for c in result['columns']]
    return [dict(zip(columns,row)) for row in result['rows']]

def assert_values(row,target):
    for name,value in target.items():
        if value is None:assert row[name] is None,(name,row[name])
        else:assert row[name] is not None and math.isclose(float(row[name]),value,rel_tol=1e-9,abs_tol=1e-9),(name,row[name],value)

def verify(root=ROOT):
    summary,paired,counts=expected_outputs(root)
    actual=load_rows('summary',root)
    keys=[(r['cohort'],r['method'],int(r['year'])) for r in actual]
    assert len(keys)==len(set(keys)) and set(keys)==set(summary)
    for key,row in zip(keys,actual):
        assert_values(row,summary[key])
        assert row['measure_kind']==('reported_12_month_ending_count' if row['method']=='december' else 'derived_mean_of_reported_snapshots')
    actual_pairs=load_rows('paired',root)
    keys=[(r['method'],int(r['year'])) for r in actual_pairs]
    assert len(keys)==len(set(keys)) and set(keys)==set(paired)
    for key,row in zip(keys,actual_pairs):assert_values(row,paired[key])
    checks=load_rows('checks',root)
    required_checks={'annual_key_or_value_mismatches','annual_duplicate_keys','quarterly_duplicate_keys','rolling_duplicate_keys','summary_duplicate_keys','paired_duplicate_keys','annual_incomplete_window_nonnull','unexpected_imputation_flag','quarterly_invalid_month_or_quarter','rolling_incomplete_window_nonnull','rolling_initial_boundary_nonnull'} | set(counts)
    assert len({r['check_name'] for r in checks})==len(checks) and {r['check_name'] for r in checks}==required_checks
    for row in checks:assert int(row['value'])==counts.get(row['check_name'],0),row
    snapshot_checks=load_rows('windows',root)
    assert {r['check_name'] for r in snapshot_checks}=={'rolling_source_or_window_mismatches','quarterly_source_mismatches'}
    assert all(int(r['value'])==0 for r in snapshot_checks)
    formats=load_rows('formats',root)
    assert {r['table_name'] for r in formats}=={n.removeprefix('rows_') for n in counts}
    assert all(r['data_source_format'].upper()=='DELTA' for r in formats)
    print(f'PASS: {len(summary)} saved summaries and {len(paired)} paired comparisons match independent source arithmetic; all five tables are Delta and all persistence/window checks pass.')
    return counts

if __name__=='__main__':
    verify()
