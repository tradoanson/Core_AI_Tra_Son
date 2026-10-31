import concurrent.futures
import json
import unittest
from core_ai_tra_son.reasoning import ReasoningEngine

class ReasoningTests(unittest.TestCase):
    def setUp(self):
        self.engine = ReasoningEngine()

    def test_unverified_fails_closed(self):
        self.assertEqual(self.engine.evaluate({"march_available": 1}).status, "UNRESOLVED")

    def test_multiple_verified_signals(self):
        r = self.engine.evaluate({"march_available": 1, "eta_seconds": 200,
            "return_buffer_seconds": 300, "resource_available": True}, verified=True)
        self.assertEqual(r.status, "REVIEW")
        self.assertEqual(r.confidence, 0.9)
        self.assertFalse(r.action_executed)

    def test_no_march_waits(self):
        self.assertEqual(self.engine.evaluate({"march_available": 0}, verified=True).status, "WAITING")

    def test_resource_unavailable_waits(self):
        r = self.engine.evaluate({"march_available": 2, "resource_available": False}, verified=True)
        self.assertEqual(r.status, "WAITING")
        self.assertIn("RESOURCE_UNAVAILABLE", r.reason_codes)

    def test_invalid_signals(self):
        for value in (True, -1, 101, "1", None):
            with self.subTest(value=value):
                self.assertEqual(self.engine.evaluate({"march_available": value}, verified=True).status, "UNRESOLVED")

    def test_nonfinite_eta(self):
        for value in (float("nan"), float("inf"), -1, 604801):
            with self.subTest(value=value):
                self.assertEqual(self.engine.evaluate({"march_available": 1, "eta_seconds": value}, verified=True).status, "UNRESOLVED")

    def test_invalid_buffer(self):
        self.assertEqual(self.engine.evaluate({"march_available": 1, "return_buffer_seconds": 3601}, verified=True).status, "UNRESOLVED")

    def test_unknown_signal_rejected(self):
        self.assertEqual(self.engine.evaluate({"march_available": 1, "citizen_id": "PRIVATE"}, verified=True).status, "UNRESOLVED")

    def test_memory_does_not_inflate_confidence(self):
        s = {"march_available": 1, "eta_seconds": 100}
        base = self.engine.evaluate(s, verified=True)
        extra = self.engine.evaluate(s, verified=True, memory_state={"namespace": "vtnd", "samples": 10, "bias_seconds": 20})
        self.assertEqual(base.confidence, extra.confidence)
        self.assertEqual(extra.evidence["adjusted_eta_seconds"], 120)

    def test_foreign_memory_ignored(self):
        r = self.engine.evaluate({"march_available": 1}, verified=True,
            memory_state={"namespace": "other", "samples": 10, "bias_seconds": 20})
        self.assertFalse(r.evidence["memory_used"])

    def test_deterministic_parallel(self):
        args = {"march_available": 2, "eta_seconds": 100, "resource_available": True}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.engine.evaluate(args, verified=True).to_dict(), range(100)))
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in results}), 1)

    def test_evidence_no_unknown_data(self):
        r = self.engine.evaluate({"march_available": 1, "eta_seconds": 10}, verified=True)
        self.assertNotIn("PRIVATE", json.dumps(r.to_dict()))

    def test_json_serializable(self):
        r = self.engine.evaluate({"march_available": 1}, verified=True)
        self.assertFalse(json.loads(json.dumps(r.to_dict()))["action_executed"])

    def test_confidence_is_bounded(self):
        for march in (0, 1, 2):
            r = self.engine.evaluate({"march_available": march}, verified=True)
            self.assertTrue(0 <= r.confidence <= 1)

if __name__ == "__main__":
    unittest.main()
