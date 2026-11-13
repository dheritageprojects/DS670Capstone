"""Regression tests for comma-formatted observed counts versus suppressed values."""
# Test historical failure and corrected parsing explicitly; never turn genuine missing counts into zero.
import json
from pathlib import Path
import unittest
import pandas as pd
from analysis.reconcile_pandas import numeric_counts,reconcile

class PandasReconciliationChecks(unittest.TestCase):
    def test_formatted_counts_and_suppression(self):
        raw=pd.Series(['1,616','12','0','',None,'Suppressed'])
        old=numeric_counts(raw,False);new=numeric_counts(raw,True)
        self.assertTrue(pd.isna(old.iloc[0]))
        self.assertEqual(new.iloc[0],1616)
        self.assertEqual(new.iloc[2],0)
        self.assertTrue(new.iloc[3:].isna().all())
        self.assertEqual(new.iloc[1],old.iloc[1])

    def test_historical_reproduction_and_change_list(self):
        root=Path(__file__).resolve().parents[1]
        recorded=json.loads((root/'analysis/pandas_reconciliation.json').read_text())
        metrics,changed,new_counties=reconcile(root)
        self.assertEqual(metrics,recorded['metrics'])
        self.assertEqual(metrics['legacy']['complete_observations'],8180)
        self.assertEqual(metrics['legacy']['complete_counties'],2385)
        self.assertEqual(metrics['legacy']['missing_overdose'],7298)
        self.assertEqual(len(changed),23)
        self.assertEqual(metrics['corrected']['complete_observations']-metrics['legacy']['complete_observations'],len(changed))
        self.assertEqual(metrics['legacy']['missing_overdose']-metrics['corrected']['missing_overdose'],len(changed))
        self.assertEqual(new_counties,['04013','06037','17031'])
        self.assertTrue(changed.source_count.str.contains(',').all())
        self.assertTrue((changed.corrected_count>=1000).all())
        self.assertFalse(changed.duplicated(['county_fips','year']).any())
