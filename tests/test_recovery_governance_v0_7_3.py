import unittest
from core_ai_tra_son.recovery_governance import RecoveryGovernance as G
from core_ai_tra_son.decision_learning import DecisionLearningState

class GovernanceTests(unittest.TestCase):
    def test_review(self):
        self.assertTrue(G.transition("PROPOSED","REVIEWED",evidence_valid=True,independent_reviewer=True).eligible)
    def test_no_unverified_review(self):
        self.assertFalse(G.transition("PROPOSED","REVIEWED",independent_reviewer=True).eligible)
    def test_approval(self):
        self.assertTrue(G.transition("REVIEWED","APPROVED",evidence_valid=True,independent_approver=True).eligible)
    def test_no_self_approval(self):
        self.assertFalse(G.transition("REVIEWED","APPROVED",evidence_valid=True).eligible)
    def test_activate(self):
        self.assertTrue(G.transition("APPROVED","ACTIVE",evidence_valid=True,override_valid=True).eligible)
    def test_no_unverified_override(self):
        self.assertFalse(G.transition("APPROVED","ACTIVE",evidence_valid=True).eligible)
    def test_close(self):
        self.assertTrue(G.transition("ACTIVE","CLOSED",closure_reviewed=True,independent_approver=True).eligible)
    def test_close_without_approval(self):
        self.assertFalse(G.transition("ACTIVE","CLOSED",closure_reviewed=True).eligible)
    def test_skip_stage(self):
        self.assertFalse(G.transition("PROPOSED","ACTIVE",evidence_valid=True,override_valid=True).eligible)
    def test_invalid_stage(self):
        with self.assertRaises(ValueError):
            G.transition("BAD","REVIEWED")
    def test_no_automatic_learning(self):
        for p in G.PHASES:
            self.assertFalse(G.learning_allowed(p))
    def test_state_validation(self):
        self.assertTrue(G.validate_recovered_state(DecisionLearningState()))
    def test_no_action(self):
        self.assertFalse(G.transition("PROPOSED","REVIEWED",evidence_valid=True,independent_reviewer=True).action_executed)
