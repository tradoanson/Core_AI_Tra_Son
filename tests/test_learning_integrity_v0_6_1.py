import concurrent.futures
import sqlite3
import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.learning_store import LearningStore
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner

class LearningIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "learning.sqlite3"
        self.store = LearningStore(self.path)
        self.store.initialize()

    def test_missing_verification_never_writes(self):
        self.assertFalse(self.store.observe("id1", "REVIEW_GATHER", successful=True))
        self.assertEqual(self.store.state().gather_samples, 0)

    def test_persists_across_instances(self):
        self.assertTrue(self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True))
        self.assertEqual(LearningStore(self.path).state().gather_adjustment, 0.02)

    def test_duplicate_exactly_once(self):
        self.assertTrue(self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True))
        self.assertFalse(self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True))
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_conflicting_duplicate_rejected(self):
        self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True)
        with self.assertRaises(ValueError):
            self.store.observe("id1", "REVIEW_GATHER", successful=False, verified=True)
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_cross_option_duplicate_rejected(self):
        self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True)
        with self.assertRaises(ValueError):
            self.store.observe("id1", "REVIEW_RETURN", successful=True, verified=True)

    def test_concurrent_same_event_once(self):
        def run(_):
            return self.store.observe("same", "REVIEW_GATHER", successful=True, verified=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(run, range(24)))
        self.assertEqual(sum(results), 1)
        self.assertEqual(self.store.state().gather_samples, 1)

    def test_concurrent_distinct_events(self):
        def run(i):
            return self.store.observe("id" + str(i), "REVIEW_GATHER", successful=True, verified=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(run, range(20)))
        self.assertEqual(sum(results), 20)
        self.assertEqual(self.store.state().gather_samples, 20)

    def test_reject_invalid_event_ids(self):
        for event_id in ("", "has spaces", "a" * 97, "name@example.com"):
            with self.subTest(event_id=event_id), self.assertRaises(ValueError):
                self.store.observe(event_id, "REVIEW_GATHER", successful=True, verified=True)

    def test_reject_nonboolean_outcome(self):
        with self.assertRaises(ValueError):
            self.store.observe("id1", "REVIEW_GATHER", successful=1, verified=True)

    def test_reject_unrecognized_existing_database(self):
        other = Path(self.temp.name) / "other.sqlite3"
        with sqlite3.connect(other) as db:
            db.execute("CREATE TABLE unrelated(id INTEGER)")
        with self.assertRaises((ValueError, sqlite3.DatabaseError, sqlite3.OperationalError)):
            LearningStore(other).initialize()

    def test_detect_tampered_hash(self):
        self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE learning_events SET event_hash='wrong' WHERE seq=1")
        with self.assertRaises(ValueError):
            self.store.state()

    def test_detect_tampered_outcome(self):
        self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE learning_events SET successful=0 WHERE seq=1")
        with self.assertRaises(ValueError):
            self.store.state()

    def test_detect_tampered_sequence(self):
        self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE learning_events SET seq=4 WHERE seq=1")
        with self.assertRaises(ValueError):
            self.store.state()

    def test_backup_restore_roundtrip(self):
        self.store.observe("id1", "REVIEW_RETURN", successful=False, verified=True)
        backup = Path(self.temp.name) / "backup.sqlite3"
        self.store.backup(backup)
        restored = LearningStore(Path(self.temp.name) / "restored.sqlite3")
        restored.restore(backup)
        self.assertEqual(restored.state(), self.store.state())
        self.assertFalse(restored.observe("id1", "REVIEW_RETURN", successful=False, verified=True))

    def test_backup_refuses_overwrite(self):
        dest = Path(self.temp.name) / "backup.sqlite3"
        self.store.backup(dest)
        with self.assertRaises(FileExistsError):
            self.store.backup(dest)

    def test_restore_refuses_overwrite(self):
        backup = Path(self.temp.name) / "backup.sqlite3"
        self.store.backup(backup)
        with self.assertRaises(FileExistsError):
            self.store.restore(backup)

    def test_corrupt_backup_rejected(self):
        bad = Path(self.temp.name) / "corrupt.sqlite3"
        bad.write_bytes(b"not sqlite")
        restored = LearningStore(Path(self.temp.name) / "restored.sqlite3")
        with self.assertRaises(sqlite3.DatabaseError):
            restored.restore(bad)
        self.assertFalse(restored.path.exists())

    def test_bad_schema_rejected(self):
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE learning_meta SET version=999")
        with self.assertRaises(ValueError):
            self.store.state()

    def test_restored_state_is_safe_for_shadow_ranking(self):
        self.store.observe("id1", "REVIEW_GATHER", successful=True, verified=True)
        state = self.store.state()
        result = AdvancedReasoner().rank({"march_available": 0}, verified=True,
                  options=["WAIT", "REVIEW_GATHER"], learning_state=state)
        self.assertEqual(result.selected, "WAIT")
        self.assertFalse(result.action_executed)

    def test_initialize_existing_valid_is_idempotent(self):
        self.store.initialize()
        self.assertEqual(self.store.state().gather_samples, 0)

if __name__ == "__main__":
    unittest.main()
