"""Append a sensitivity page to a freshly exported dashboard, preserving all other pages."""
# Construct controls and charts on one shared live, read-only SQL dataset.
import json
from pathlib import Path
import sys

DATASET = 'sensitivity_live'
def frame(title, description=''):
    return {'title':title,'showTitle':True,'description':description,'showDescription':bool(description)}
def build_page():
    layout=[]
    def add(name,spec,fields,x,y,w=3,h=5,raw=False):
        layout.append({'widget':{'name':'sensitivity_'+name,'queries':[{'name':'main_query','query':{'datasetName':DATASET,'fields':[{'name':n,'expression':e} for n,e in fields],'disaggregated':raw}}],'spec':spec},'position':dict(x=x,y=y,width=w,height=h)})
    layout.append({'widget':{'name':'sensitivity_intro','textbox_spec':'# Does the annualization method change the picture?\nDecember is a reported count. Other methods are strict means of overlapping reported snapshots, not annual death estimates. Suppression in any required period makes a smoothed measure missing. Available cohorts vary by method. Shared-within-year and fixed-all-years comparisons use identical counties; fixed cohorts may overrepresent larger counties. Filters select from those precomputed cohorts. Counts are not population-adjusted; associations are ecological, not causal.'},'position':dict(x=0,y=0,width=6,height=4)})
    for x,(field,title) in enumerate([('year','Year'),('state','State'),('county_fips','County FIPS')]):
        add('filter_'+field,{'version':2,'widgetType':'filter-multi-select','frame':frame(title),'encodings':{'fields':[{'fieldName':field,'queryName':'main_query'}]}},[(field,f'`{field}`')],x*2,4,2,2)
    def chart(name,title,expr,x,y,description):
        fields=[('year','`year`'),('method','`method`'),('value',expr)]
        add(name,{'version':3,'widgetType':'line','frame':frame(title,description),'encodings':{'x':{'fieldName':'year','scale':{'type':'categorical'}},'y':{'fieldName':'value','scale':{'type':'quantitative'}},'color':{'fieldName':'method','scale':{'type':'categorical'}}}},fields,x,y)
    chart('coverage','Complete county-years by method','SUM(CAST(`complete_case` AS INT))',0,6,'Requires both dispensing and the overdose measure; strict smoothing may reduce coverage.')
    chart('available_means','Mean overdose measure: available complete cases','AVG(CASE WHEN `complete_case` THEN `overdose_measure` END)',3,6,'Unweighted means on method-specific county cohorts; differences may reflect selection.')
    chart('shared_means','Mean overdose measure: shared counties within each year','AVG(CASE WHEN `common_within_year` THEN `overdose_measure` END)',0,11,'All four methods and dispensing available; county membership can change between years.')
    chart('fixed_means','Mean overdose measure: fixed counties across all five years','AVG(CASE WHEN `common_all_years` THEN `overdose_measure` END)',3,11,'All four methods and dispensing available for 2020–2024; same cohort for every line and year.')
    chart('differences','Paired mean difference from December','AVG(CASE WHEN `complete_case` AND `december_count` IS NOT NULL THEN `overdose_measure` - `december_count` END)',0,16,'Pairs use identical county-years within each method; paired cohorts differ between methods.')
    chart('missing','Missing overdose measures by method','SUM(CASE WHEN `overdose_measure` IS NULL THEN 1 ELSE 0 END)',3,16,'Includes strict-window missingness; no suppressed count is zero-filled.')
    columns=['state','county_fips','year','method','overdose_measure','dispensing_rate','complete_case','common_within_year','common_all_years']
    add('details',{'version':2,'widgetType':'table','frame':frame('Sensitivity county-year details'),'encodings':{'columns':[{'fieldName':c} for c in columns]}},[(c,f'`{c}`') for c in columns],0,21,6,7,True)
    return {'name':'annualization_sensitivity','displayName':'Annualization sensitivity','layout':layout}

# Merge only the named sensitivity dataset/page into the immediately exported current draft.
def merge(current):
    sql=Path(__file__).with_name('sensitivity_dataset.sql').read_text()
    assert not any(d['name']==DATASET for d in current.get('datasets',[])), 'Sensitivity dataset already exists; inspect before replacing.'
    assert not any(p['name']=='annualization_sensitivity' for p in current.get('pages',[])), 'Sensitivity page already exists.'
    current['datasets'].append({'name':DATASET,'displayName':'Strict snapshot sensitivity (live source Volume)','query':sql})
    current['pages'].append(build_page())
    return current

if __name__=='__main__':
    current=json.loads(Path(sys.argv[1]).read_text())
    Path(sys.argv[2]).write_text(json.dumps(merge(current),indent=2)+'\n')
