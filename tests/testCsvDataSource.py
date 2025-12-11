import os
import tempfile
import unittest
from datetime import datetime

from finance.core.coreTypes import DataValidationError
from finance.data.csvDataSource import CsvDataSource


class TestCsvDataSource(unittest.TestCase):
    def test_load_sorts_by_date(self):
        csv = """date,open,high,low,close,volume
2025-01-03,10,11,9,10,100
2025-01-01,8,9,7,8,100
2025-01-02,9,10,8,9,100
"""
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write(csv)

            ds = CsvDataSource()
            r = ds.load(symbol="TEST", csv_path=p)
            dts = [b.dt.date().isoformat() for b in r.bars]
            self.assertEqual(dts, ["2025-01-01", "2025-01-02", "2025-01-03"])

    def test_duplicate_date_raises(self):
        csv = """date,open,high,low,close,volume
2025-01-01,10,11,9,10,100
2025-01-01,10,11,9,10,100
"""
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write(csv)

            ds = CsvDataSource()
            with self.assertRaises(DataValidationError):
                ds.load(symbol="TEST", csv_path=p)
