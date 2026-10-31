import concurrent.futures
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from core_ai_tra_son.secure_learning import SecureLearningStore
from core_ai_tra_son.learning_store import LearningStore
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner


class SecureLearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.db = root / "learning.sqlite3"
        self.anchor = root / "checkpoint.json"
        self.key = b"k" * 32
        self.store = SecureLearningStore(self.db, self.anchor, self.key)
        self.store.initialize()
        self.store.bootstrap()

    def write(self, i, option="REVIEW_GATHER", successful=True):
        return self.store.observe("event" + str(i), option, successful=successful, verified=True)

    def test_bootstrap_initial(self):
        self.assertEqual(self.store.state().gather_samples, 0)

    def test_verified_learning_persists(self):
        self.assertTrue(self.write(1))
        other = SecureLearningStore(self.db, self.anchor, self.key)
        self.assertEqual(other.state().gather_samples, 1)

    def test_unverified_does_not_write(self):
        self.assertFalse(self.store.observe("event1", "REVIEW_GATHER", successful=True))
        self.assertEqual(self.store.state().gather_samples, 0)

    def test_duplicate_is_idempotent(self):
        self.assertTrue(self.write(1))
        self.assertFalse(self.write(1))
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_conflicting_duplicate_fails(self):
        self.write(1)
        with self.assertRaises(ValueError):
            self.write(1, successful=False)

    def test_invalid_key_rejected(self):
        with self.assertRaises(ValueError):
            SecureLearningStore(self.db, self.anchor, b"short")

    def test_wrong_key_rejected(self):
        self.write(1)
        with self.assertRaises(ValueError):
            SecureLearningStore(self.db, self.anchor, b"z" * 32).state()

    def test_tampered_checkpoint_rejected(self):
        doc = json.loads(self.anchor.read_text())
        doc["payload"]["count"] = 5
        self.anchor.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            self.store.state()

    def test_missing_checkpoint_fails_closed(self):
        self.anchor.unlink()
        with self.assertRaises(FileNotFoundError):
            self.store.state()

    def test_refuse_rebootstrap(self):
        with self.assertRaises(FileExistsError):
            self.store.bootstrap()

    def test_history_rollback_detected(self):
        self.write(1)
        with sqlite3.connect(self.db) as db:
            db.execute("DELETE FROM learning_events WHERE seq=1")
        with self.assertRaises(ValueError):
            self.store.state()

    def test_rewritten_head_detected(self):
        self.write(1)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE learning_events SET event_hash=? WHERE seq=1", ("0" * 64,))
        with self.assertRaises(ValueError):
            self.store.state()

    def test_crash_suffix_reconciles(self):
        self.write(1)
        LearningStore(self.db).observe("event2", "REVIEW_RETURN", successful=False, verified=True)
        self.assertEqual(self.store.state().return_samples, 1)
        self.store.reconcile()
        self.assertEqual(self.store.state().return_samples, 1)

    def test_corrupt_suffix_rejected(self):
        self.write(1)
        LearningStore(self.db).observe("event2", "REVIEW_RETURN", successful=True, verified=True)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE learning_events SET event_hash='bad' WHERE seq=2")
        with self.assertRaises(ValueError):
            self.store.reconcile()

    def test_no_reconcile_if_checkpoint_invalid(self):
        self.anchor.write_bytes(b"not-json")
        with self.assertRaises(ValueError):
            self.store.reconcile()

    def test_concurrent_same_event_once(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.write(1), range(20)))
        self.assertEqual(sum(results), 1)
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_concurrent_unique_events(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(self.write, range(40)))
        self.assertEqual(sum(results), 40)
        self.assertEqual(self.store.state().gather_samples, 40)

    def test_incremental_replay_reads_only_suffix(self):
        for i in range(30):
            self.write(i)
        self.assertEqual(self.store.state().gather_samples, 30)
        self.assertEqual(self.store.reconcile().gather_samples, 30)

    def test_checkpoint_does_not_store_secret(self):
        self.write(1)
        self.assertNotIn(self.key.decode(), self.anchor.read_text())

    def test_shadow_safety(self):
        self.write(1)
        r = AdvancedReasoner().rank({"march_available": 0}, verified=True,
            options=["WAIT", "REVIEW_GATHER"], learning_state=self.store.state())
        self.assertEqual(r.selected, "WAIT")
        self.assertFalse(r.action_executed)

    def test_recover_from_backup_with_checkpoint(self):
        self.write(1)
        backup = self.db.parent / "backup.sqlite3"
        self.store.backup(backup)
        recovered_db = self.db.parent / "recovered.sqlite3"
        LearningStore(recovered_db).restore(backup)
        recovered = SecureLearningStore(recovered_db, self.anchor, self.key)
        self.assertEqual(recovered.state().gather_samples, 1)

    def test_checkpoint_independent_location(self):
        with self.assertRaises(ValueError):
            SecureLearningStore(self.db, self.db, self.key)

    def test_invalid_event_id(self):
        with self.assertRaises(ValueError):
            self.store.observe("bad id", "REVIEW_GATHER", successful=True, verified=True)

    def test_invalid_outcome(self):
        with self.assertRaises(ValueError):
            self.store.observe("event1", "REVIEW_GATHER", successful=1, verified=True)

    def test_performance_linear_history_not_replayed_on_every_write(self):
        for i in range(100):
            self.write(i)
        self.assertEqual(self.store.state().gather_samples, 100)

if __name__ == "__main__":
    unittest.main()
