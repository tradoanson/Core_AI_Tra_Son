import unittest
from core_ai_tra_son.candidate_gate import REQUIRED,evaluate_candidate

class CandidateGateTests(unittest.TestCase):
    def test_empty_blocked(self):self.assertEqual(evaluate_candidate({}).status,"BLOCKED")
    def test_all_missing(self):self.assertEqual(evaluate_candidate({}).missing,REQUIRED)
    def test_all_true_review(self):self.assertEqual(evaluate_candidate(dict.fromkeys(REQUIRED,True)).status,"READY_FOR_REVIEW")
    def test_failed_blocks(self):self.assertEqual(evaluate_candidate(dict.fromkeys(REQUIRED,False)).status,"BLOCKED")
    def test_one_missing_blocks(self):self.assertEqual(evaluate_candidate(dict.fromkeys(REQUIRED[:-1],True)).status,"BLOCKED")
    def test_unknown_rejected(self):
        with self.assertRaises(ValueError):evaluate_candidate({"invented":True})
    def test_nonbool_rejected(self):
        with self.assertRaises(ValueError):evaluate_candidate({"linux_311":1})
    def test_no_action(self):self.assertFalse(evaluate_candidate({}).action_executed)
