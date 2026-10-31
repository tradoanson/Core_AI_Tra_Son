import unittest
from core_ai_tra_son.decision_quality_audit import audit_synthetic_decisions
class QualityAuditTests(unittest.TestCase):
    def test_pass(self):self.assertEqual(audit_synthetic_decisions().status,"PASS")
    def test_count(self):self.assertEqual(audit_synthetic_decisions().total,5)
    def test_matched(self):self.assertEqual(audit_synthetic_decisions().matched,5)
    def test_agreement(self):self.assertEqual(audit_synthetic_decisions().agreement_rate,1.0)
    def test_no_mismatches(self):self.assertFalse(audit_synthetic_decisions().mismatch_ids)
    def test_synthetic(self):self.assertEqual(audit_synthetic_decisions().dataset_kind,"SYNTHETIC")
    def test_no_actions(self):self.assertFalse(audit_synthetic_decisions().action_executed)
