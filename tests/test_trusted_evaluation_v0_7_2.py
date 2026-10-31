import json
import os
import tempfile
import unittest
from pathlib import Path

from core_ai_tra_son.trusted_evaluation import (
    TrustedEvaluationStore, issue_provenance, approve_rollback, holdout_digest)
from core_ai_tra_son.decision_quality import DecisionCase
from core_ai_tra_son.decision_learning import DecisionLearningState
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner


@unittest.skipUnless(os.name == "posix", "POSIX flock only")
class TrustedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.store = TrustedEvaluationStore(root/"ledger.sqlite3", root/"anchor.json",
            b"l"*32, root/"evaluation.json", root/"override.json",
            issuer_key=b"i"*32, approver_key=b"a"*32)
        self.store.initialize()
        self.store.bootstrap()
        self.signals = {"march_available":2, "resource_available":True,
                        "eta_seconds":100, "return_buffer_seconds":300}

    def train(self):
        for i in range(4):
            self.store.observe("train_g"+str(i), "REVIEW_GATHER", successful=True, verified=True)
            self.store.observe("train_r"+str(i), "REVIEW_RETURN", successful=False, verified=True)

    def cases(self, label="REVIEW_RETURN"):
        return [DecisionCase("holdout"+str(i), dict(self.signals), label) for i in range(8)]

    def evaluate(self):
        cases = self.cases()
        proof = issue_provenance(cases, issuer_id="independent-issuer", issuer_key=b"i"*32)
        return self.store.evaluate_trusted(cases, proof)

    def degraded(self):
        self.train()
        self.assertEqual(self.evaluate().status, "DEGRADED")

    def approved(self, count=0):
        request = self.store.rollback_request(count)
        approval = approve_rollback(request, approver_id="independent-approver", approver_key=b"a"*32)
        return request, approval

    def test_trusted_provenance_evaluates(self):
        self.degraded()
        self.assertEqual(self.store.verify_evaluation()["report"]["status"], "DEGRADED")

    def test_untrusted_issuer_fails(self):
        self.train()
        cases = self.cases()
        proof = issue_provenance(cases, issuer_id="issuer", issuer_key=b"z"*32)
        with self.assertRaises(ValueError):
            self.store.evaluate_trusted(cases, proof)

    def test_tampered_holdout_fails(self):
        self.train()
        cases = self.cases()
        proof = issue_provenance(cases, issuer_id="issuer", issuer_key=b"i"*32)
        cases[0] = DecisionCase("changed", dict(self.signals), "REVIEW_RETURN")
        with self.assertRaises(ValueError):
            self.store.evaluate_trusted(cases, proof)

    def test_tampered_signature_fails(self):
        self.train()
        cases = self.cases()
        proof = issue_provenance(cases, issuer_id="issuer", issuer_key=b"i"*32)
        proof["signature"] = "0"*64
        with self.assertRaises(ValueError):
            self.store.evaluate_trusted(cases, proof)

    def test_no_provenance_fails(self):
        self.train()
        with self.assertRaises(ValueError):
            self.store.evaluate_trusted(self.cases(), None)

    def test_training_overlap_still_fails(self):
        self.train()
        cases = self.cases()
        cases[0] = DecisionCase("train_g0", dict(self.signals), "REVIEW_RETURN")
        proof = issue_provenance(cases, issuer_id="issuer", issuer_key=b"i"*32)
        with self.assertRaises(ValueError):
            self.store.evaluate_trusted(cases, proof)

    def test_distinct_keys_required(self):
        root = Path(self.tmp.name)
        with self.assertRaises(ValueError):
            TrustedEvaluationStore(root/"ledger.sqlite3", root/"anchor.json",
                b"l"*32, root/"evaluation.json", root/"override.json",
                issuer_key=b"l"*32, approver_key=b"a"*32)

    def test_invalid_issuer(self):
        with self.assertRaises(ValueError):
            issue_provenance(self.cases(), issuer_id="bad issuer", issuer_key=b"i"*32)

    def test_invalid_approver(self):
        self.degraded()
        request = self.store.rollback_request(0)
        with self.assertRaises(ValueError):
            approve_rollback(request, approver_id="bad approver", approver_key=b"a"*32)

    def test_rollback_replayed_genesis(self):
        self.degraded()
        request, approval = self.approved()
        self.assertEqual(self.store.activate_trusted_rollback(request, approval), DecisionLearningState())
        self.assertEqual(self.store.effective_state(), DecisionLearningState())

    def test_rollback_replayed_prefix(self):
        self.degraded()
        request, approval = self.approved(2)
        state = self.store.activate_trusted_rollback(request, approval)
        self.assertEqual((state.gather_samples, state.return_samples), (1, 1))

    def test_rollback_survives_new_instance(self):
        self.degraded()
        request, approval = self.approved(0)
        self.store.activate_trusted_rollback(request, approval)
        other = TrustedEvaluationStore(self.store.path, self.store.checkpoint_path,
            b"l"*32, self.store.evaluation_path, self.store.override_path,
            issuer_key=b"i"*32, approver_key=b"a"*32)
        self.assertEqual(other.effective_state(), DecisionLearningState())

    def test_wrong_approver_fails(self):
        self.degraded()
        request = self.store.rollback_request(0)
        approval = approve_rollback(request, approver_id="approver", approver_key=b"z"*32)
        with self.assertRaises(ValueError):
            self.store.activate_trusted_rollback(request, approval)

    def test_wrong_request_fails(self):
        self.degraded()
        request, approval = self.approved(0)
        request = dict(request)
        request["count"] = 1
        with self.assertRaises(ValueError):
            self.store.activate_trusted_rollback(request, approval)

    def test_untrusted_previous_state_forbidden(self):
        self.degraded()
        with self.assertRaises(ValueError):
            self.store.activate_rollback(DecisionLearningState())

    def test_stale_request_fails(self):
        self.degraded()
        request, approval = self.approved(0)
        self.store.observe("later", "REVIEW_GATHER", successful=True, verified=True)
        with self.assertRaises(ValueError):
            self.store.activate_trusted_rollback(request, approval)

    def test_future_target_fails(self):
        self.degraded()
        with self.assertRaises(ValueError):
            self.store.rollback_request(8)

    def test_negative_target_fails(self):
        self.degraded()
        with self.assertRaises(ValueError):
            self.store.rollback_request(-1)

    def test_rollback_freezes_learning(self):
        self.degraded()
        request, approval = self.approved(0)
        self.store.activate_trusted_rollback(request, approval)
        with self.assertRaises(ValueError):
            self.store.observe("next", "REVIEW_GATHER", successful=True, verified=True)

    def test_rollback_does_not_delete_history(self):
        self.degraded()
        count = self.store.state().gather_samples
        request, approval = self.approved(0)
        self.store.activate_trusted_rollback(request, approval)
        self.assertEqual(self.store.state().gather_samples, count)

    def test_report_contains_no_raw_signals(self):
        self.degraded()
        self.assertNotIn("march_available", self.store.evaluation_path.read_text())

    def test_provenance_has_no_raw_signals(self):
        proof = issue_provenance(self.cases(), issuer_id="issuer", issuer_key=b"i"*32)
        self.assertNotIn("march_available", json.dumps(proof))

    def test_holdout_digest_deterministic(self):
        self.assertEqual(holdout_digest(self.cases()), holdout_digest(self.cases()))

    def test_shadow_no_actions(self):
        self.degraded()
        request, approval = self.approved(0)
        self.store.activate_trusted_rollback(request, approval)
        ranked = AdvancedReasoner().rank({"march_available":0}, verified=True,
                    options=["WAIT","REVIEW_GATHER"], learning_state=self.store.effective_state())
        self.assertEqual(ranked.selected, "WAIT")
        self.assertFalse(ranked.action_executed)

    def test_missing_approval_fails(self):
        self.degraded()
        with self.assertRaises(ValueError):
            self.store.activate_trusted_rollback(self.store.rollback_request(0), None)

if __name__ == "__main__":
    unittest.main()
