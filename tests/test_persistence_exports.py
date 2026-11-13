"""Regression check for the complete saved Databricks sensitivity persistence evidence."""
# Independently reproduce saved summaries/paired differences and require zero readback mismatches.
import unittest
from analysis.verify_sensitivity_exports import verify

class DeltaPersistenceEvidenceChecks(unittest.TestCase):
    def test_saved_databricks_outputs(self):
        verify()
