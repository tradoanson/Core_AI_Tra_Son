import concurrent.futures
import json
import unittest
from core_ai_tra_son.reasoning import ReasoningEngine
from core_ai_tra_son.validation import BenchmarkCase, validate_benchmark

FIXTURES = [
    BenchmarkCase("empty", {"march_available": 0}, True, "WAITING"),
    BenchmarkCase("available", {"march_available": 2}, True, "REVIEW"),
    BenchmarkCase("full_signals", {"march_available": 1, "eta_seconds": 30,
        "return_buffer_seconds": 300, "resource_available": True}, True, "REVIEW"),
    BenchmarkCase("no_resource", {"march_available": 2, "resource_available": False}, True, "WAITING"),
    BenchmarkCase("capacity_equal", {"march_available": 3, "march_capacity": 3}, True, "REVIEW"),
    BenchmarkCase("capacity_conflict", {"march_available": 4, "march_capacity": 3}, True, "UNRESOLVED"),
    BenchmarkCase("zero_capacity", {"march_available": 0, "march_capacity": 0}, True, "WAITING"),
    BenchmarkCase("unverified", {"march_available": 2}, False, "UNRESOLVED"),
    BenchmarkCase("invalid_march", {"march_available": -1}, True, "UNRESOLVED"),
    BenchmarkCase("invalid_eta", {"march_available": 1, "eta_seconds": -1}, True, "UNRESOLVED"),
    BenchmarkCase("invalid_capacity", {"march_available": 2, "march_capacity": True}, True, "UNRESOLVED"),
    BenchmarkCase("unknown_signal", {"march_available": 1, "person": "PRIVATE"}, True, "UNRESOLVED"),
]

class ReasoningValidationTests(unittest.TestCase):
    def test_reference_cases_all_match(self):
        report = validate_benchmark(FIXTURES)
        self.assertEqual(report.total, 12)
        self.assertEqual(report.matched, 12)
        self.assertEqual(report.agreement, 1.0)

    def test_conflict_fails_closed(self):
        result = ReasoningEngine().evaluate({"march_available": 5, "march_capacity": 4}, verified=True)
        self.assertEqual(result.status, "UNRESOLVED")
        self.assertEqual(result.confidence, 0)
        self.assertEqual(result.reason_codes, ("SIGNAL_CONFLICT",))
        self.assertFalse(result.action_executed)

    def test_capacity_boundary(self):
        for capacity in (0, 1, 100):
            result = ReasoningEngine().evaluate({"march_available": capacity, "march_capacity": capacity}, verified=True)
            self.assertNotEqual(result.status, "UNRESOLVED")

    def test_invalid_capacity(self):
        for capacity in (-1, 101, True, 1.5, "5"):
            result = ReasoningEngine().evaluate({"march_available": 1, "march_capacity": capacity}, verified=True)
            self.assertEqual(result.status, "UNRESOLVED")

    def test_conflict_has_no_evidence_leak(self):
        result = ReasoningEngine().evaluate({"march_available": 3, "march_capacity": 2}, verified=True)
        self.assertEqual(result.evidence, {})

    def test_mismatch_report_identifiers_only(self):
        cases = [BenchmarkCase("case_1", {"march_available": 0}, True, "REVIEW")]
        report = validate_benchmark(cases)
        self.assertEqual(report.mismatches, ("case_1",))
        self.assertEqual(report.agreement, 0)

    def test_report_has_confidence_bins(self):
        report = validate_benchmark(FIXTURES)
        self.assertIn("0.0", report.by_confidence)
        self.assertIn("0.6", report.by_confidence)
        self.assertIn("0.9", report.by_confidence)

    def test_repeated_runs_identical(self):
        outputs = [validate_benchmark(FIXTURES).to_dict() for _ in range(20)]
        self.assertTrue(all(output == outputs[0] for output in outputs))

    def test_parallel_reports_identical(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda _: validate_benchmark(FIXTURES).to_dict(), range(50)))
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in outputs}), 1)

    def test_case_count_bounds(self):
        with self.assertRaises(ValueError):
            validate_benchmark([])
        with self.assertRaises(ValueError):
            validate_benchmark(FIXTURES * 50)

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            validate_benchmark([FIXTURES[0], FIXTURES[0]])

    def test_invalid_case_id_rejected(self):
        with self.assertRaises(ValueError):
            validate_benchmark([BenchmarkCase("private person name", {"march_available": 0}, True, "WAITING")])

    def test_unverified_never_review(self):
        for march in (0, 1, 3, 100):
            self.assertEqual(ReasoningEngine().evaluate({"march_available": march}, verified=False).status, "UNRESOLVED")

    def test_confidence_does_not_claim_probability(self):
        report = validate_benchmark(FIXTURES)
        self.assertTrue(all(0 <= row["agreement"] <= 1 for row in report.by_confidence.values()))

    def test_no_input_mutation(self):
        signals = {"march_available": 3, "march_capacity": 2}
        before = repr(signals)
        ReasoningEngine().evaluate(signals, verified=True)
        self.assertEqual(repr(signals), before)

if __name__ == "__main__":
    unittest.main()
