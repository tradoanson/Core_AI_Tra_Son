import concurrent.futures
import json
import unittest
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner

class DecisionQualityTests(unittest.TestCase):
    def setUp(self):
        self.engine = AdvancedReasoner()
        self.options = ["WAIT", "REVIEW_GATHER", "REVIEW_RETURN"]

    def rank(self, signals, options=None, **kwargs):
        return self.engine.rank(signals, verified=True, options=self.options if options is None else options, **kwargs)

    def test_unknown_resource_cannot_promote_gather(self):
        r = self.rank({"march_available": 2}, options=["WAIT", "REVIEW_GATHER"])
        self.assertEqual(r.selected, "WAIT")
        self.assertEqual(r.alternatives[-1].score, 0)

    def test_resource_false_cannot_promote_return(self):
        r = self.rank({"march_available": 2, "resource_available": False,
                       "eta_seconds": 1, "return_buffer_seconds": 300})
        self.assertEqual(r.selected, "WAIT")
        self.assertEqual(next(x for x in r.alternatives if x.option == "REVIEW_RETURN").score, 0)

    def test_resource_true_promotes_gather(self):
        r = self.rank({"march_available": 2, "resource_available": True},
                      options=["WAIT", "REVIEW_GATHER"])
        self.assertEqual(r.selected, "REVIEW_GATHER")

    def test_due_return_outweighs_gather(self):
        r = self.rank({"march_available": 2, "resource_available": True,
                       "eta_seconds": 300, "return_buffer_seconds": 300})
        self.assertEqual(r.selected, "REVIEW_RETURN")

    def test_return_later_than_buffer_loses_to_gather(self):
        r = self.rank({"march_available": 2, "resource_available": True,
                       "eta_seconds": 301, "return_buffer_seconds": 300})
        self.assertEqual(r.selected, "REVIEW_GATHER")

    def test_zero_march_waits_even_if_return_due(self):
        r = self.rank({"march_available": 0, "resource_available": True,
                       "eta_seconds": 0, "return_buffer_seconds": 300})
        self.assertEqual(r.selected, "WAIT")

    def test_all_blocked_fails_closed(self):
        r = self.rank({"march_available": 0}, options=["REVIEW_GATHER", "REVIEW_RETURN"])
        self.assertEqual(r.status, "UNRESOLVED")
        self.assertIsNone(r.selected)

    def test_memory_bias_changes_ranking_without_inflating_confidence(self):
        signals = {"march_available": 2, "resource_available": True,
                   "eta_seconds": 290, "return_buffer_seconds": 300}
        a = self.rank(signals)
        b = self.rank(signals, memory_state={"namespace": "vtnd", "samples": 3, "bias_seconds": 20})
        self.assertEqual(a.selected, "REVIEW_RETURN")
        self.assertEqual(b.selected, "REVIEW_GATHER")
        self.assertEqual(a.confidence, b.confidence)

    def test_explanation_identifies_selected_and_reason(self):
        r = self.rank({"march_available": 2, "resource_available": True})
        self.assertIn(r.selected, r.explanation)
        self.assertIn("score", r.explanation)
        self.assertTrue(all(x.explanation for x in r.alternatives))

    def test_blocked_alternative_explains_why(self):
        r = self.rank({"march_available": 2})
        gather = next(x for x in r.alternatives if x.option == "REVIEW_GATHER")
        self.assertIn("blocked", gather.explanation.lower())

    def test_input_permutation_stable(self):
        s = {"march_available": 2, "resource_available": True, "eta_seconds": 1, "return_buffer_seconds": 5}
        a = self.rank(s).to_dict()
        b = self.rank(s, options=list(reversed(self.options))).to_dict()
        self.assertEqual(a, b)

    def test_parallel_stability(self):
        s = {"march_available": 2, "resource_available": True, "eta_seconds": 1, "return_buffer_seconds": 5}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.rank(s).to_dict(), range(100)))
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in results}), 1)

    def test_unknown_fields_fail_closed(self):
        r = self.rank({"march_available": 2, "private": "SECRET"})
        self.assertEqual(r.status, "UNRESOLVED")
        self.assertNotIn("SECRET", json.dumps(r.to_dict()))

    def test_unverified_rejects_ranking(self):
        r = self.engine.rank({"march_available": 2}, verified=False, options=self.options)
        self.assertEqual(r.status, "UNRESOLVED")

    def test_conflict_rejects_ranking(self):
        r = self.rank({"march_available": 3, "march_capacity": 2})
        self.assertEqual(r.status, "UNRESOLVED")

    def test_all_recommendations_never_execute(self):
        for march in (0, 1, 2):
            r = self.rank({"march_available": march, "resource_available": True})
            self.assertFalse(r.action_executed)

if __name__ == "__main__":
    unittest.main()
