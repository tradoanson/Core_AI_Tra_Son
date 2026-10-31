"""Concurrent writes, consistent backups, corruption refusal and safe recovery."""
import concurrent.futures
import sqlite3
import tempfile
import unittest
from pathlib import Path

from core_ai_tra_son.memory import AdaptiveMemory


class MemoryResilienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "adaptive.db"
        self.memory = AdaptiveMemory(self.path, "vtnd", alpha=0.2)
        self.memory.initialize()

    def test_parallel_verified_writers_preserve_sample_count(self):
        def work(i):
            m = AdaptiveMemory(self.path, "vtnd")
            return m.observe(100, 110, verified=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(work, range(60)))
        self.assertTrue(all(results))
        self.assertEqual(self.memory.state()["samples"], 60)

    def test_parallel_namespace_isolation(self):
        def work(i):
            name = "vtnd" if i % 2 else "nhankhau"
            return AdaptiveMemory(self.path, name).observe(100, 120, verified=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            self.assertTrue(all(pool.map(work, range(40))))
        self.assertEqual(self.memory.state()["samples"], 20)
        self.assertEqual(AdaptiveMemory(self.path, "nhankhau").state()["samples"], 20)

    def test_backup_and_restore_preserve_data(self):
        self.memory.observe(100, 120, verified=True)
        backup = self.root / "snapshot.db"
        self.assertEqual(self.memory.backup(backup), backup)
        self.assertTrue(backup.exists())
        self.path.unlink()
        self.memory.restore(backup)
        self.assertEqual(self.memory.state()["samples"], 1)

    def test_backup_does_not_overwrite(self):
        dest = self.root / "existing.db"
        dest.write_bytes(b"sentinel")
        with self.assertRaises(FileExistsError):
            self.memory.backup(dest)
        self.assertEqual(dest.read_bytes(), b"sentinel")

    def test_restore_does_not_overwrite_live_database(self):
        backup = self.root / "backup.db"
        self.memory.backup(backup)
        with self.assertRaises(FileExistsError):
            self.memory.restore(backup)
        self.assertEqual(self.memory.state()["samples"], 0)

    def test_corrupt_database_fails_closed(self):
        self.path.write_bytes(b"not a sqlite database")
        with self.assertRaises(sqlite3.DatabaseError):
            self.memory.state()
        with self.assertRaises(sqlite3.DatabaseError):
            self.memory.backup(self.root / "bad-copy.db")
        self.assertFalse((self.root / "bad-copy.db").exists())

    def test_corrupt_backup_never_creates_target(self):
        backup = self.root / "bad-backup.db"
        backup.write_bytes(b"corrupt")
        self.path.unlink()
        with self.assertRaises(sqlite3.DatabaseError):
            self.memory.restore(backup)
        self.assertFalse(self.path.exists())

    def test_backup_snapshot_consistent_under_writes(self):
        def writer(i):
            return AdaptiveMemory(self.path, "vtnd").observe(100, 110, verified=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(writer, i) for i in range(40)]
            snapshot = self.root / "parallel-snapshot.db"
            self.memory.backup(snapshot)
            self.assertTrue(all(f.result() for f in futures))
        with sqlite3.connect(snapshot) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            count = db.execute("SELECT samples FROM adaptive_state WHERE namespace='vtnd'").fetchone()
            self.assertTrue(count is None or 0 <= count[0] <= 40)
        self.assertEqual(self.memory.state()["samples"], 40)

    def test_missing_database_read_is_noncreating(self):
        self.path.unlink()
        self.assertEqual(self.memory.state()["samples"], 0)
        self.assertFalse(self.path.exists())

    def test_invalid_backup_source_rejected(self):
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.memory.backup(self.root / "snapshot.db")

if __name__ == "__main__":
    unittest.main()
