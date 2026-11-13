"""Small independent tests of the statistical reference, including tied observations."""
# Verify known ranks and associations rather than copying implementation expressions.
import unittest
from analysis.reference import average_ranks, correlation

class CorrelationChecks(unittest.TestCase):
    def test_ties(self):
        self.assertEqual(average_ranks([30,10,10,20]), [4,1.5,1.5,3])

    def test_monotonic_nonlinear(self):
        x, y = [1,2,3,4], [1,4,9,16]
        self.assertAlmostEqual(correlation(average_ranks(x),average_ranks(y)), 1)
        self.assertLess(correlation(x,y), 1)

    def test_constant_or_small(self):
        self.assertIsNone(correlation([1,1], [2,3]))
        self.assertIsNone(correlation([1], [2]))

    def test_reverse(self):
        self.assertAlmostEqual(correlation([1,2,3], [3,2,1]), -1)

# Compare complete exported Databricks results with independently parsed source snapshots.
import json
import math
from pathlib import Path
from analysis.reference import summaries, geographic_summaries

class ExportedResultChecks(unittest.TestCase):
    def compare_rows(self, name, expected, keys):
        root=Path(__file__).resolve().parents[1]
        result=json.loads((root/'analysis'/f'{name}_results.json').read_text())
        columns=[c['name'] for c in result['columns']]
        rows=[dict(zip(columns,row)) for row in result['rows']]
        self.assertFalse(result['truncated'])
        self.assertEqual(result['total_row_count'],len(rows))
        lookup={tuple(str(row[k]) for k in keys):row for row in expected}
        self.assertEqual(len(rows),len(lookup))
        self.assertEqual({tuple(str(row[k]) for k in keys) for row in rows},set(lookup))
        for row in rows:
            target=lookup[tuple(str(row[k]) for k in keys)]
            for key,value in target.items():
                if key in keys:
                    continue
                if value is None:
                    self.assertIsNone(row[key])
                else:
                    self.assertTrue(math.isclose(float(row[key]),value,rel_tol=1e-10,abs_tol=1e-10),(name,key,row[key],value))

    def test_association_exports(self):
        self.compare_rows('associations',summaries(Path(__file__).resolve().parents[1]),['cohort','method','year'])

    def test_geographic_exports(self):
        self.compare_rows('geographic',geographic_summaries(Path(__file__).resolve().parents[1]),['state','year'])
