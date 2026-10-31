import concurrent.futures
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from core_ai_tra_son.hardened_learning import HardenedLearningStore
from core_ai_tra_son.learning_store import LearningStore
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner


@unittest.skipUnless(os.name == "posix", "POSIX flock only")
class HardenedLearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.db = root / "learning.sqlite3"
        self.checkpoint = root / "checkpoint.json"
        self.store = HardenedLearningStore(self.db, self.checkpoint, b"k" * 32)
        self.store.initialize()
        self.store.bootstrap()

    def write(self, i):
        return self.store.observe("id" + str(i), "REVIEW_GATHER", successful=True, verified=True)

    def child(self, code):
        return subprocess.run([sys.executable, "-c", code, str(self.db), str(self.checkpoint)],
                              capture_output=True, text=True, timeout=25)

    def test_initial_empty(self):
        self.assertEqual(self.store.state().gather_samples, 0)

    def test_single_write(self):
        self.assertTrue(self.write(1))
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_duplicate_same_instance(self):
        self.assertTrue(self.write(1))
        self.assertFalse(self.write(1))

    def test_multiple_instances_sequential(self):
        other = HardenedLearningStore(self.db, self.checkpoint, b"k" * 32)
        self.write(1)
        self.assertTrue(other.observe("id2", "REVIEW_RETURN", successful=False, verified=True))
        self.assertEqual(self.store.state().return_samples, 1)

    def test_parallel_threads(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            result = list(pool.map(self.write, range(40)))
        self.assertEqual(sum(result), 40)
        self.assertEqual(self.store.state().gather_samples, 40)

    def test_parallel_independent_instances(self):
        def job(i):
            s = HardenedLearningStore(self.db, self.checkpoint, b"k" * 32)
            return s.observe("id" + str(i), "REVIEW_GATHER", successful=True, verified=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            result = list(pool.map(job, range(30)))
        self.assertEqual(sum(result), 30)
        self.assertEqual(self.store.state().gather_samples, 30)

    def test_parallel_processes_unique(self):
        code = ("import sys; from core_ai_tra_son.hardened_learning import HardenedLearningStore;"
                "s=HardenedLearningStore(sys.argv[1],sys.argv[2],b'k'*32);"
                "assert s.observe('child'+sys.argv[3],'REVIEW_GATHER',successful=True,verified=True)")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda i: subprocess.run(
                [sys.executable, "-c", code, str(self.db), str(self.checkpoint), str(i)],
                capture_output=True, text=True, timeout=30), range(8)))
        self.assertTrue(all(p.returncode == 0 for p in results), [p.stderr for p in results])
        self.assertEqual(self.store.state().gather_samples, 8)

    def test_parallel_processes_duplicate(self):
        code = ("import sys; from core_ai_tra_son.hardened_learning import HardenedLearningStore;"
                "s=HardenedLearningStore(sys.argv[1],sys.argv[2],b'k'*32);"
                "s.observe('same','REVIEW_GATHER',successful=True,verified=True)")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.child(code), range(6)))
        self.assertTrue(all(p.returncode == 0 for p in results), [p.stderr for p in results])
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_crash_after_commit_before_checkpoint(self):
        # Reproduce a committed ledger event with an older authenticated anchor.
        self.write(1)
        code = ("import sys,os; from core_ai_tra_son.learning_store import LearningStore;"
                "LearningStore(sys.argv[1]).observe('crashed','REVIEW_RETURN',successful=True,verified=True);"
                "os._exit(7)")
        result = self.child(code)
        self.assertEqual(result.returncode, 7)
        self.assertTrue(self.write(2))
        state = self.store.state()
        self.assertEqual((state.gather_samples, state.return_samples), (2, 1))

    def test_reconcile_valid_suffix(self):
        self.write(1)
        LearningStore(self.db).observe("suffix", "REVIEW_RETURN", successful=True, verified=True)
        self.assertEqual(self.store.reconcile().return_samples, 1)

    def test_corrupt_suffix_blocks_new_write(self):
        self.write(1)
        LearningStore(self.db).observe("suffix", "REVIEW_RETURN", successful=True, verified=True)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE learning_events SET event_hash='bad' WHERE seq=2")
        with self.assertRaises(ValueError):
            self.write(2)

    def test_missing_checkpoint_blocks_new_write(self):
        self.checkpoint.unlink()
        with self.assertRaises(FileNotFoundError):
            self.write(1)

    def test_wrong_key_blocks_read(self):
        other = HardenedLearningStore(self.db, self.checkpoint, b"z" * 32)
        with self.assertRaises(ValueError):
            other.state()

    def test_no_unverified_write(self):
        self.assertFalse(self.store.observe("id1", "REVIEW_GATHER", successful=True))
        self.assertEqual(self.store.state().gather_samples, 0)

    def test_lock_file_is_not_removed(self):
        self.write(1)
        self.assertTrue(Path(str(self.checkpoint) + ".lock").is_file())

    def test_bounded_history_performance_smoke(self):
        # Not a throughput guarantee; small synthetic growth regression.
        for i in range(100):
            self.write(i)
        start = time.monotonic()
        for i in range(100, 200):
            self.write(i)
        elapsed = time.monotonic() - start
        self.assertEqual(self.store.state().gather_samples, 200)
        self.assertLess(elapsed, 30)

    def test_shadow_never_executes(self):
        self.write(1)
        result = AdvancedReasoner().rank({"march_available": 0}, verified=True,
            options=["WAIT", "REVIEW_GATHER"], learning_state=self.store.state())
        self.assertEqual(result.selected, "WAIT")
        self.assertFalse(result.action_executed)

    def test_tampered_checkpoint_blocks(self):
        self.write(1)
        doc = json.loads(self.checkpoint.read_text())
        doc["payload"]["count"] = 0
        self.checkpoint.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            self.store.state()

    def test_lock_symlink_rejected(self):
        lock = Path(str(self.checkpoint) + ".lock")
        lock.unlink()
        lock.symlink_to(self.db)
        with self.assertRaises(OSError):
            self.store.state()

if __name__ == "__main__":
    unittest.main()
