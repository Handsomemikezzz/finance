import unittest

from finance.indicators.smaIndicator import compute_sma_series


class TestSmaIndicator(unittest.TestCase):
    def test_sma_series_alignment(self):
        values = [1, 2, 3, 4]
        sma = compute_sma_series(values, window=3)
        self.assertEqual(sma[0], None)
        self.assertEqual(sma[1], None)
        self.assertAlmostEqual(sma[2], 2.0)
        self.assertAlmostEqual(sma[3], 3.0)
