import concurrent.futures
import json
import unittest
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner

class AdvancedReasoningTests(unittest.TestCase):
    def setUp(self):
        self.r = AdvancedReasoner()

    def test_rank_three_options(self):
        x = self.r.rank({"march_available": 2, "eta_seconds": 20,
                         "return_buffer_seconds": 300, "resource_available": True},
                        verified=True, options=["WAIT", "REVIEW_GATHER", "REVIEW_RETURN"])
        self.assertEqual(x.selected, "REVIEW_RETURN")
        self.assertEqual([o.rank for o in x.alternatives], [1, 2, 3])
        self.assertFalse(x.action_executed)

    def test_wait_when_no_march(self):
        x = self.r.rank({"march_available": 0}, verified=True, options=["WAIT", "REVIEW_GATHER"])
        self.assertEqual(x.selected, "WAIT")
        self.assertEqual(x.status, "WAITING")

    def test_resource_unavailable_blocks_gather(self):
        x = self.r.rank({"march_available": 2, "resource_available": False},
                        verified=True, options=["WAIT", "REVIEW_GATHER"])
        self.assertEqual(x.selected, "WAIT")

    def test_unverified_withholds_ranking(self):
        x = self.r.rank({"march_available": 2}, verified=False, options=["WAIT", "REVIEW_GATHER"])
        self.assertEqual(x.status, "UNRESOLVED")
        self.assertEqual(x.alternatives, ())

    def test_conflict_withholds_ranking(self):
        x = self.r.rank({"march_available": 3, "march_capacity": 2},
                        verified=True, options=["WAIT", "REVIEW_GATHER"])
        self.assertEqual(x.status, "UNRESOLVED")

    def test_duplicate_options_rejected(self):
        self.assertEqual(self.r.rank({"march_available": 1}, verified=True,
                                    options=["WAIT", "WAIT"]).status, "UNRESOLVED")

    def test_unknown_option_rejected(self):
        self.assertEqual(self.r.rank({"march_available": 1}, verified=True,
                                    options=["DISPATCH"]).status, "UNRESOLVED")

    def test_missing_options_rejected(self):
        self.assertEqual(self.r.rank({"march_available": 1}, verified=True).status, "UNRESOLVED")

    def test_return_requires_eta_and_buffer(self):
        x = self.r.rank({"march_available": 2}, verified=True, options=["REVIEW_RETURN"])
        self.assertEqual(x.status, "UNRESOLVED")

    def test_tie_order_independent(self):
        s = {"march_available": 1}
        a = self.r.rank(s, verified=True, options=["WAIT", "REVIEW_GATHER"]).to_dict()
        b = self.r.rank(s, verified=True, options=["REVIEW_GATHER", "WAIT"]).to_dict()
        self.assertEqual(a, b)

    def test_no_private_data_in_output(self):
        x = self.r.rank({"march_available": 1, "citizen_id": "SECRET"},
                        verified=True, options=["WAIT"])
        self.assertNotIn("SECRET", json.dumps(x.to_dict()))

    def test_memory_does_not_inflate_confidence(self):
        signals = {"march_available": 1, "eta_seconds": 100, "return_buffer_seconds": 100}
        a = self.r.rank(signals, verified=True, options=["WAIT", "REVIEW_RETURN"])
        b = self.r.rank(signals, verified=True, options=["WAIT", "REVIEW_RETURN"],
                        memory_state={"namespace": "vtnd", "samples": 5, "bias_seconds": 5})
        self.assertEqual(a.confidence, b.confidence)

    def test_parallel_determinism(self):
        s = {"march_available": 2, "eta_seconds": 30, "return_buffer_seconds": 300}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda _: self.r.rank(s, verified=True,
                            options=["WAIT", "REVIEW_RETURN", "REVIEW_GATHER"]).to_dict(), range(100)))
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in outputs}), 1)

    def test_serialization(self):
        x = self.r.rank({"march_available": 0}, verified=True, options=["WAIT"])
        self.assertFalse(json.loads(json.dumps(x.to_dict()))["action_executed"])

    def test_invalid_option_container(self):
        self.assertEqual(self.r.rank({"march_available": 1}, verified=True,
                                    options={"WAIT"}).status, "UNRESOLVED")

if __name__ == "__main__":
    unittest.main()
