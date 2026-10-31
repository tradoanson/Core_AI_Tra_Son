import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.evaluation_integrity import EvaluationIntegrityStore
from core_ai_tra_son.decision_quality import DecisionCase
from core_ai_tra_son.decision_learning import DecisionLearningState
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner


@unittest.skipUnless(os.name == "posix", "POSIX checkpoint locking only")
class EvaluationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.store = EvaluationIntegrityStore(root/"learning.sqlite3", root/"anchor.json",
                                              b"k"*32, root/"evaluation.json", root/"override.json")
        self.store.initialize()
        self.store.bootstrap()
        self.signals = {"march_available": 2, "resource_available": True,
                        "eta_seconds": 100, "return_buffer_seconds": 300}

    def train(self):
        for i in range(4):
            self.store.observe("train_g"+str(i), "REVIEW_GATHER", successful=True, verified=True)
            self.store.observe("train_r"+str(i), "REVIEW_RETURN", successful=False, verified=True)

    def holdout(self, expected="REVIEW_RETURN"):
        return [DecisionCase("holdout"+str(i), dict(self.signals), expected) for i in range(8)]

    def test_signed_evaluation_pass(self):
        self.train()
        report = self.store.evaluate_holdout(self.holdout("REVIEW_GATHER"))
        self.assertEqual(report.status, "PASS")
        self.assertEqual(self.store.verify_evaluation()["report"]["status"], "PASS")

    def test_signed_evaluation_degraded(self):
        self.train()
        report = self.store.evaluate_holdout(self.holdout())
        self.assertEqual(report.status, "DEGRADED")

    def test_training_overlap_rejected(self):
        self.train()
        cases = self.holdout()
        cases[0] = DecisionCase("train_g0", dict(self.signals), "REVIEW_RETURN")
        with self.assertRaises(ValueError):
            self.store.evaluate_holdout(cases)

    def test_duplicate_holdout_rejected(self):
        cases = self.holdout()
        cases[1] = cases[0]
        with self.assertRaises(ValueError):
            self.store.evaluate_holdout(cases)

    def test_unverified_holdout_rejected(self):
        cases = self.holdout()
        cases[0] = DecisionCase("unverified", dict(self.signals), "REVIEW_RETURN", verified=False)
        with self.assertRaises(ValueError):
            self.store.evaluate_holdout(cases)

    def test_tampered_report_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        path = self.store.evaluation_path
        doc = json.loads(path.read_text())
        doc["payload"]["report"]["status"] = "PASS"
        path.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            self.store.verify_evaluation()

    def test_wrong_key_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        other = EvaluationIntegrityStore(self.store.path, self.store.checkpoint_path, b"z"*32,
                                         self.store.evaluation_path, self.store.override_path)
        with self.assertRaises(ValueError):
            other.verify_evaluation()

    def test_report_create_only(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        with self.assertRaises(FileExistsError):
            self.store.evaluate_holdout(self.holdout())

    def test_stale_report_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.observe("later", "REVIEW_GATHER", successful=True, verified=True)
        with self.assertRaises(ValueError):
            self.store.verify_evaluation()

    def test_persistent_rollback_effective_state(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        previous = DecisionLearningState()
        self.store.activate_rollback(previous)
        self.assertEqual(self.store.effective_state(), previous)
        other = EvaluationIntegrityStore(self.store.path, self.store.checkpoint_path, b"k"*32,
                                         self.store.evaluation_path, self.store.override_path)
        self.assertEqual(other.effective_state(), previous)

    def test_rollback_does_not_rewrite_ledger(self):
        self.train()
        count = self.store.state().gather_samples
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        self.assertEqual(self.store.state().gather_samples, count)

    def test_rollback_freezes_learning(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        with self.assertRaises(ValueError):
            self.store.observe("new", "REVIEW_GATHER", successful=True, verified=True)

    def test_no_rollback_without_degradation(self):
        self.train()
        self.store.evaluate_holdout(self.holdout("REVIEW_GATHER"))
        with self.assertRaises(ValueError):
            self.store.activate_rollback(DecisionLearningState())

    def test_rollback_newer_state_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        future = DecisionLearningState(gather_samples=100)
        with self.assertRaises(ValueError):
            self.store.activate_rollback(future)

    def test_rollback_create_only(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        with self.assertRaises(FileExistsError):
            self.store.activate_rollback(DecisionLearningState())

    def test_tampered_override_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        doc = json.loads(self.store.override_path.read_text())
        doc["payload"]["state"]["gather_adjustment"] = 0.08
        self.store.override_path.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            self.store.effective_state()

    def test_missing_evaluation_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        self.store.evaluation_path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.store.effective_state()

    def test_stale_override_rejected(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        with sqlite3.connect(self.store.path) as db:
            db.execute("DELETE FROM learning_events WHERE seq=8")
        with self.assertRaises(ValueError):
            self.store.effective_state()

    def test_invalid_paths(self):
        with self.assertRaises(ValueError):
            EvaluationIntegrityStore(self.store.path, self.store.checkpoint_path, b"k"*32,
                                     self.store.path, self.store.override_path)

    def test_report_does_not_contain_raw_signals(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.assertNotIn("march_available", self.store.evaluation_path.read_text())

    def test_shadow_safety(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        self.store.activate_rollback(DecisionLearningState())
        result = AdvancedReasoner().rank({"march_available":0}, verified=True,
                   options=["WAIT","REVIEW_GATHER"], learning_state=self.store.effective_state())
        self.assertEqual(result.selected, "WAIT")
        self.assertFalse(result.action_executed)

    def test_no_rollback_if_report_missing(self):
        with self.assertRaises(FileNotFoundError):
            self.store.activate_rollback(DecisionLearningState())

    def test_empty_ledger_holdout(self):
        report = self.store.evaluate_holdout(self.holdout())
        self.assertEqual(report.status, "PASS")

    def test_immutable_previous(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        previous = DecisionLearningState()
        self.store.activate_rollback(previous)
        self.assertEqual(previous.gather_samples, 0)

    def test_signed_report_has_digest(self):
        self.train()
        self.store.evaluate_holdout(self.holdout())
        payload = self.store.verify_evaluation()
        self.assertEqual(len(payload["holdout_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
