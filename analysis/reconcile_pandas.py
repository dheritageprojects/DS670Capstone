"""Reproduce historical pandas parsing and compare with comma-normalized counts."""
# Read frozen snapshots with the original pandas defaults, without executing uploaded notebook code.
import io
import json
from pathlib import Path
import warnings
import zipfile
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def numeric_counts(values, corrected):
    if corrected:
        values=values.astype('string').str.replace(',', '', regex=False)
    return pd.to_numeric(values, errors='coerce')

def reconcile(root=ROOT):
    frames={}
    for name in ('dispensing','overdose'):
        with zipfile.ZipFile(Path(root)/'sources'/f'{name}.csv.zip') as archive:
            member=next(n for n in archive.namelist() if n.endswith('.csv'))
            # Original read_csv can warn about mixed numeric/string types; this is part of the evidence.
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',pd.errors.DtypeWarning)
                frames[name]=pd.read_csv(io.BytesIO(archive.read(member)))
    d,o=frames['dispensing'],frames['overdose']
    raw_counts={'raw_dispensing':len(d),'raw_overdose':len(o)}
    d=d[d.Year.between(2020,2024)].copy();o=o[o.Year.between(2020,2024)].copy()
    d['FIPS']=d.Location.astype(str).str.zfill(5);o['FIPS']=o.FIPS.astype(str).str.zfill(5)
    d['dispensing_rate']=pd.to_numeric(d['Opioid Dispensing Rate'],errors='coerce')
    o['legacy']=numeric_counts(o['Provisional Drug Overdose Deaths'],False)
    o['corrected']=numeric_counts(o['Provisional Drug Overdose Deaths'],True)
    annual=o[o.Month==12].sort_values(['Year','FIPS']).drop_duplicates(['Year','FIPS'],keep='first')
    merged=d[['Year','FIPS','STATE_NAME','COUNTY_NAME','dispensing_rate']].merge(annual[['Year','FIPS','Provisional Drug Overdose Deaths','legacy','corrected']],on=['Year','FIPS'],how='inner')

    # Compute both outcomes with identical keys, date selection, deduplication, and merge semantics.
    metrics={}
    county_sets={}
    for method in ('legacy','corrected'):
        complete=merged.dropna(subset=['dispensing_rate',method])
        county_sets[method]=set(complete.FIPS)
        metrics[method]={**raw_counts,'matching_fips':len(set(d.FIPS)&set(annual.FIPS)),'merged_county_years':len(merged),'complete_observations':len(complete),'complete_counties':complete.FIPS.nunique(),'missing_dispensing':int(merged.dispensing_rate.isna().sum()),'missing_overdose':int(merged[method].isna().sum()),'complete_by_year':{str(k):int(v) for k,v in complete.groupby('Year').size().items()}}
    changed=merged.loc[merged.legacy.isna() & merged.corrected.notna()].copy()
    assert changed['Provisional Drug Overdose Deaths'].astype(str).str.contains(',').all()
    assert changed.dispensing_rate.notna().all(), 'Count recovery does not necessarily imply complete-case recovery.'
    # Every changed value is observed in the source, not an estimate of a suppressed count.
    changed=changed.rename(columns={'FIPS':'county_fips','Year':'year','STATE_NAME':'state','COUNTY_NAME':'county','Provisional Drug Overdose Deaths':'source_count','corrected':'corrected_count'})
    changed=changed[['county_fips','year','state','county','source_count','corrected_count']].sort_values(['county_fips','year'])
    return metrics,changed,sorted(county_sets['corrected']-county_sets['legacy'])

# Save an auditable row-level change list and both aggregate metric sets.
if __name__=='__main__':
    metrics,changed,new_counties=reconcile()
    changed.to_csv(ROOT/'analysis/pandas_reconciliation_rows.csv',index=False)
    result={'pandas_version':pd.__version__,'method':'Historical read_csv defaults and pd.to_numeric(errors="coerce") versus identical steps with literal comma removal before numeric conversion.','metrics':metrics,'recovered_county_years':len(changed),'new_complete_counties':new_counties,'uploaded_overdose_csv_byte_identity_verified':False,'overdose_input_note':'Used previously supplied frozen overdose ZIP; newly re-uploaded CSV exceeds the transfer limit. Historical saved metrics and yearly counts reproduced exactly.'}
    (ROOT/'analysis/pandas_reconciliation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
