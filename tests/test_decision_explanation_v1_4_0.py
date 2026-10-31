import unittest
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner, RankingResult
from core_ai_tra_son.decision_explanation import explain_ranking
class ExplanationTests(unittest.TestCase):
    def rank(self): return AdvancedReasoner().rank({"march_available":0},verified=True,options=["WAIT","REVIEW_GATHER"])
    def test_selected(self): self.assertEqual(explain_ranking(self.rank()).selected,"WAIT")
    def test_blocked(self): self.assertIn("REVIEW_GATHER",explain_ranking(self.rank()).rejected)
    def test_uncalibrated(self): self.assertEqual(explain_ranking(self.rank()).confidence_kind,"HEURISTIC_UNCALIBRATED")
    def test_unresolved(self):
        r=AdvancedReasoner().rank({"march_available":1},verified=False,options=["WAIT"])
        self.assertEqual(explain_ranking(r).status,"UNRESOLVED")
    def test_no_action(self): self.assertFalse(explain_ranking(self.rank()).action_executed)
    def test_reject_invalid(self):
        with self.assertRaises(ValueError): explain_ranking(None)
    def test_reject_inconsistent(self):
        r=RankingResult("REVIEW",0.5,"WAIT",(),"",())
        with self.assertRaises(ValueError): explain_ranking(r)
