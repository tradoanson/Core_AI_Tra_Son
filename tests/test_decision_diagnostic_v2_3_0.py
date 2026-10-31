import unittest
from core_ai_tra_son.decision_diagnostic import diagnose_decision

class DiagnosticTests(unittest.TestCase):
    def test_unverified(self):self.assertEqual(diagnose_decision({"march_available":0}).status,"UNRESOLVED")
    def test_wait(self):self.assertEqual(diagnose_decision({"march_available":0},verified=True).selected,"WAIT")
    def test_margin(self):self.assertGreaterEqual(diagnose_decision({"march_available":0},verified=True).margin,0)
    def test_conflict(self):self.assertIn("GATHER_BLOCKED",diagnose_decision({"march_available":0},verified=True).conflict_codes)
    def test_no_action(self):self.assertFalse(diagnose_decision({"march_available":0},verified=True).action_executed)
    def test_uncalibrated(self):self.assertEqual(diagnose_decision({"march_available":0},verified=True).confidence_kind,"HEURISTIC_UNCALIBRATED")
    def test_invalid(self):
        with self.assertRaises(ValueError):diagnose_decision(None)
