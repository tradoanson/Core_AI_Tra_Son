import sqlite3
import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.integrity_probe import inspect_sqlite_copy

class IntegrityProbeTests(unittest.TestCase):
    def test_valid(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"copy.sqlite3"
            with sqlite3.connect(p) as db:db.execute("CREATE TABLE x (v INTEGER)")
            result=inspect_sqlite_copy(p)
            self.assertEqual(result.status,"PASS")
            self.assertFalse(result.action_executed)
    def test_missing(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(inspect_sqlite_copy(Path(d)/"absent.db").status,"BLOCKED")
    def test_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"copy.db";p.write_bytes(b"not sqlite")
            self.assertEqual(inspect_sqlite_copy(p).status,"BLOCKED")
    def test_bad_path(self):
        with self.assertRaises(ValueError):inspect_sqlite_copy(None)
    def test_oversized(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"big.db"
            with p.open("wb") as f:f.truncate(64*1024*1024+1)
            self.assertEqual(inspect_sqlite_copy(p).status,"BLOCKED")
