"""Build a reproducible Databricks AI/BI dashboard definition from verified tables."""
# Define one row-level dataset so year, state, and county filters share the same scope.
import json
from pathlib import Path
DATASET = 'county_panel'
datasets = [{'name': DATASET, 'displayName': 'County-year coverage panel', 'query': 'SELECT *, CAST(missing_dispensing AS INT) AS missing_dispensing_n, CAST(missing_overdose AS INT) AS missing_overdose_n FROM workspace.capstone.county_year'}, {'name': 'quality', 'displayName': 'Unfiltered pipeline validation', 'query': 'SELECT * FROM workspace.capstone.quality_report'}]
layout = []
def frame(title, description=''):
    return dict(title=title, showTitle=True, description=description, showDescription=bool(description))
def query(fields, dataset=DATASET, disaggregated=False):
    return [{'name': 'main_query', 'query': {'datasetName': dataset, 'fields': [{'name': n, 'expression': e} for n,e in fields], 'disaggregated': disaggregated}}]
def add(name, spec, fields, x, y, w=3, h=5, dataset=DATASET, disaggregated=False):
    layout.append({'widget': {'name': name, 'queries': query(fields,dataset,disaggregated), 'spec':spec}, 'position':dict(x=x,y=y,width=w,height=h)})
def chart(name, kind, dimension, metric, expression, title, x,y, description='', numeric_x=False):
    fields=[(dimension,f'`{dimension}`'),(metric,expression)]
    spec={'version':3,'widgetType':kind,'frame':frame(title,description),'encodings':{'x':{'fieldName':dimension,'scale':{'type':'quantitative' if numeric_x else 'categorical'}},'y':{'fieldName':metric,'scale':{'type':'quantitative'}}}}
    add(name,spec,fields,x,y)
# Add methodology text and shared field filters without imputing any values.
layout.append({'widget':{'name':'intro','textbox_spec':'# U.S. Opioid Dispensing and Overdose Trends | 2020–2024\nDecember reported 12-month-ending overdose counts; suppressed values stay missing. Counts are not population-adjusted death rates. County dispensing means are unweighted, not state/national rates. Observed death subtotals depend on reporting coverage. Association does not establish causation. County identifiers are FIPS codes. Historical differences are explained by comma-formatted counts discarded by the original pandas parser.'},'position':dict(x=0,y=0,width=6,height=3)})
for x,(field,title) in enumerate([('year','Year'),('state','State'),('county_fips','County FIPS')]):
    add('filter_'+field,{'version':2,'widgetType':'filter-multi-select','frame':frame(title),'encodings':{'fields':[{'fieldName':field,'queryName':'main_query'}]}},[(field,f'`{field}`')],x*2,3,2,2)
# Define trends, reporting coverage, geographic comparisons, and missingness charts.
chart('dispensing_trend','line','year','mean_dispensing','AVG(`dispensing_rate`)','Mean county dispensing rate per 100 persons',0,5,'Unweighted mean among counties with reported dispensing.')
chart('overdose_trend','line','year','observed_deaths','SUM(`overdose_count`)','Reported overdose deaths: observed-county subtotal',3,5,'Coverage varies; do not interpret as national totals.')
chart('reporting_coverage','bar','year','reporting_counties','COUNT(`overdose_count`)','County-years with reported overdose counts',0,10)
chart('missing_overdose','bar','year','missing_counties','SUM(`missing_overdose_n`)','County-years missing overdose counts',3,10)
chart('state_dispensing','bar','state','mean_dispensing','AVG(`dispensing_rate`)','State comparison: mean county dispensing',0,15,'Unweighted county mean; use state filter to focus.')
chart('state_overdose','bar','state','observed_deaths','SUM(`overdose_count`)','State comparison: reported overdose subtotal',3,15,'Across selected years; excludes missing counties.')
# Keep county/year in the scatter query to retain one observation per county-year.
scatter_fields=[(n,f'`{n}`') for n in ['county_fips','year','state']]+[('dispensing_rate','CASE WHEN `complete_case` THEN `dispensing_rate` END'),('overdose_count','CASE WHEN `complete_case` THEN `overdose_count` END')]
add('association',{'version':3,'widgetType':'scatter','frame':frame('Dispensing vs reported overdose count','Complete observations only; count depends on population. No causal interpretation.'),'encodings':{'x':{'fieldName':'dispensing_rate','scale':{'type':'quantitative'}},'y':{'fieldName':'overdose_count','scale':{'type':'quantitative'}}}},scatter_fields,0,20,3,5,disaggregated=True)
chart('missing_dispensing','bar','year','missing_counties','SUM(`missing_dispensing_n`)','County-years missing dispensing rates',3,20)
# Show detailed county comparisons and unfiltered quality differences in tables.
cols=['state','county_fips','year','dispensing_rate','overdose_count','missing_dispensing','missing_overdose']
add('county_details',{'version':2,'widgetType':'table','frame':frame('County-year details'),'encodings':{'columns':[{'fieldName':c} for c in cols]}},[(c,f'`{c}`') for c in cols],0,25,6,7,disaggregated=True)
cols=['metric','actual','target','difference']
add('quality_report',{'version':2,'widgetType':'table','frame':frame('Pipeline validation — not affected by dashboard filters','Historical pandas conversion discarded 23 comma-formatted reported counts; current values retain them.'),'encodings':{'columns':[{'fieldName':c} for c in cols]}},[(c,f'`{c}`') for c in cols],0,32,6,5,dataset='quality',disaggregated=True)
# Save the complete draft definition; publishing is a separate action.
definition={'datasets':datasets,'pages':[{'name':'overview','displayName':'County trends and coverage','layout':layout}]}
if __name__=='__main__':
    Path(__file__).with_name('opioid_trends.lvdash.json').write_text(json.dumps(definition,indent=2)+'\n')
