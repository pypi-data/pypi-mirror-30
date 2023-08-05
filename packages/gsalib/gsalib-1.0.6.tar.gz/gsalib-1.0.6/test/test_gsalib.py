# -*- coding: utf-8 -*-

"""
Tests for gsalib
"""

import os
import unittest

from gsalib import GatkReport, GsalibException

this_dir = os.path.dirname(os.path.realpath(__file__))

test_bad = os.path.join(this_dir, 'hs_metrics.txt')
test_v10 = os.path.join(this_dir, 'test_v1.0_gatkreport.table')
test_v11 = os.path.join(this_dir, 'test_v1.1.grp')
test_v01 = os.path.join(this_dir, 'test_v0.1.table')
test_v02 = os.path.join(this_dir, 'test_v0.2.table')


def read_report(filename):
    return GatkReport(filename)


class TestGsalibGatkReportBadInput(unittest.TestCase):
    """
    gsalib does not recognize Picard samtools.metrics data
    """
    def test(self):
        with self.assertRaises(GsalibException):
            report = read_report(test_bad)


class TestGsalibGatkReportV11(unittest.TestCase):
    def setUp(self):
        self.data = read_report(test_v11).tables

    def test_table_count(self):
        self.assertEqual(len(self.data), 5)

    def test_table_names(self):
        self.assertEqual(sorted(list(self.data.keys())),
                         sorted([
                            'GenotypeConcordance_CompProportions',
                            'GenotypeConcordance_Counts',
                            'GenotypeConcordance_EvalProportions',
                            'GenotypeConcordance_Summary',
                            'SiteConcordance_Summary']))

    def test_table_sizes(self):
        self.assertEqual(self.data['GenotypeConcordance_CompProportions'].values.size, 40)
        self.assertEqual(self.data['GenotypeConcordance_Counts'].values.size, 76)
        self.assertEqual(self.data['GenotypeConcordance_EvalProportions'].values.size, 40)
        self.assertEqual(self.data['GenotypeConcordance_Summary'].values.size, 12)
        self.assertEqual(self.data['SiteConcordance_Summary'].values.size, 6)


class TestGsalibGatkReportV10Report(unittest.TestCase):
    def setUp(self):
        self.data = read_report(test_v10).tables

    def test_table_count(self):
        self.assertEqual(len(self.data), 2)

    def test_table_names(self):
        self.assertEqual(list(self.data.keys()),  ['ErrorRatePerCycle', 'ExampleTable'])

    def test_table_sizes(self):
        self.assertEqual(self.data['ErrorRatePerCycle'].values.size, 27)
        self.assertEqual(self.data['ExampleTable'].values.size, 6)


class TestGsalibGatkReportV01Report(unittest.TestCase):
    def setUp(self):
        self.data = read_report(test_v01).tables

    def test_table_count(self):
        self.assertEqual(len(self.data), 1)

    def test_table_names(self):
        self.assertEqual(list(self.data.keys()),  ['CompOverlap'])

    def test_table_sizes(self):
        self.assertEqual(self.data['CompOverlap'].values.size, 36)


class TestGsalibGatkReportV02Report(unittest.TestCase):
    def setUp(self):
        self.data = read_report(test_v02).tables

    def test_table_count(self):
        self.assertEqual(len(self.data), 5)

    def test_table_names(self):
        self.assertEqual(sorted(list(self.data.keys())),
                         sorted([
                             'CompOverlap',
                             'CountVariants',
                             'TiTvVariantEvaluator',
                             'ValidationReport',
                             'VariantSummary']))

    def test_table_sizes(self):
        self.assertEqual(self.data['CompOverlap'].values.size, 33)
        self.assertEqual(self.data['CountVariants'].values.size, 90)
        self.assertEqual(self.data['TiTvVariantEvaluator'].values.size, 42)
        self.assertEqual(self.data['ValidationReport'].values.size, 72)
        self.assertEqual(self.data['VariantSummary'].values.size, 60)


if __name__ == '__main__':
    unittest.main()
