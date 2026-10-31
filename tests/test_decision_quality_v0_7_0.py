import concurrent.futures
import json
import unittest
from core_ai_tra_son.decision_quality import DecisionCase, evaluate_quality, rollback_on_degradation
from core_ai_tra_son.decision_learning import DecisionLearningState, DecisionLearner
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner


def sample(i, expected="REVIEW_GATHER", *, signals=None):
    return DecisionCase("case" + str(i), signals or {
        "march_available": 2, "resource_available": True,
        "eta_seconds": 100, "return_buffer_seconds": 300}, expected)


class DecisionQualityTests(unittest.TestCase):
    def setUp(self):
        self.previous = DecisionLearningState()
        self.learned = DecisionLearningState(gather_adjustment=0.08,
                                            return_adjustment=-0.08,
                                            gather_samples=4, return_samples=4)
        self.cases = [sample(i) for i in range(10)]

    def test_baseline_accuracy(self):
        r = evaluate_quality(self.cases, self.previous)
        self.assertEqual(r.baseline_accuracy, 0)
        self.assertEqual(r.adapted_accuracy, 0)
        self.assertEqual(r.status, "PASS")

    def test_adapted_improves(self):
        r = evaluate_quality(self.cases, self.learned)
        self.assertEqual(r.baseline_correct, 0)
        self.assertEqual(r.adapted_correct, 10)
        self.assertEqual(r.delta, 1.0)
        self.assertEqual(len(r.improvements), 10)
        self.assertEqual(r.status, "PASS")

    def test_degradation_detected(self):
        cases = [sample(i, "REVIEW_RETURN") for i in range(10)]
        r = evaluate_quality(cases, self.learned)
        self.assertEqual(r.status, "DEGRADED")
        self.assertEqual(len(r.regressions), 10)

    def test_rollback_restores_previous(self):
        r = evaluate_quality([sample(i, "REVIEW_RETURN") for i in range(10)], self.learned)
        self.assertIs(rollback_on_degradation(self.learned, self.previous, r), self.previous)

    def test_pass_keeps_current(self):
        r = evaluate_quality(self.cases, self.learned)
        self.assertIs(rollback_on_degradation(self.learned, self.previous, r), self.learned)

    def test_budget_allows_limited_regression(self):
        cases = [sample(i, "REVIEW_RETURN") if i == 0 else sample(i) for i in range(10)]
        r = evaluate_quality(cases, self.learned, max_regressions=1)
        self.assertEqual(r.status, "PASS")
        self.assertEqual(len(r.regressions), 1)

    def test_strict_regression_budget(self):
        cases = [sample(i, "REVIEW_RETURN") if i == 0 else sample(i) for i in range(10)]
        self.assertEqual(evaluate_quality(cases, self.learned).status, "DEGRADED")

    def test_delta_threshold(self):
        r = evaluate_quality(self.cases, self.previous, min_delta=0.1)
        self.assertEqual(r.status, "DEGRADED")

    def test_reject_too_few_cases(self):
        with self.assertRaises(ValueError):
            evaluate_quality(self.cases[:7], self.learned)

    def test_reject_too_many_cases(self):
        with self.assertRaises(ValueError):
            evaluate_quality([sample(i) for i in range(513)], self.learned)

    def test_reject_duplicate_ids(self):
        with self.assertRaises(ValueError):
            evaluate_quality([sample(1) for _ in range(8)], self.learned)

    def test_reject_unverified_case(self):
        cases = list(self.cases)
        cases[0] = DecisionCase("unverified", {}, "WAIT", verified=False)
        with self.assertRaises(ValueError):
            evaluate_quality(cases, self.learned)

    def test_reject_unknown_expected(self):
        cases = list(self.cases)
        cases[0] = sample(0, "EXECUTE")
        with self.assertRaises(ValueError):
            evaluate_quality(cases, self.learned)

    def test_reject_invalid_state(self):
        with self.assertRaises(ValueError):
            evaluate_quality(self.cases, DecisionLearningState(gather_adjustment=100))

    def test_reject_invalid_threshold(self):
        for value in (float("nan"), float("inf"), "0.1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate_quality(self.cases, self.learned, min_delta=value)

    def test_conflicting_signal_abstains(self):
        cases = [sample(i, signals={"march_available": 3, "march_capacity": 2}) for i in range(10)]
        r = evaluate_quality(cases, self.learned)
        self.assertEqual(r.status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(r.abstained), 10)

    def test_abstention_not_counted_as_error(self):
        cases = self.cases[:8] + [sample(8, signals={"march_available": 3, "march_capacity": 2})]
        r = evaluate_quality(cases, self.learned)
        self.assertEqual(r.evaluated, 8)
        self.assertEqual(len(r.abstained), 1)

    def test_insufficient_evidence_blocks_rollback(self):
        cases = [sample(i, signals={"march_available": 3, "march_capacity": 2}) for i in range(10)]
        r = evaluate_quality(cases, self.learned)
        with self.assertRaises(ValueError):
            rollback_on_degradation(self.learned, self.previous, r)

    def test_no_host_action(self):
        self.assertFalse(evaluate_quality(self.cases, self.learned).action_executed)

    def test_report_serializes_without_signals(self):
        s = json.dumps(evaluate_quality(self.cases, self.learned).to_dict())
        self.assertNotIn("march_available", s)
        self.assertIn("improvements", s)

    def test_order_independent(self):
        a = evaluate_quality(self.cases, self.learned)
        b = evaluate_quality(list(reversed(self.cases)), self.learned)
        self.assertEqual(a.delta, b.delta)
        self.assertEqual(a.adapted_correct, b.adapted_correct)

    def test_parallel_determinism(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: evaluate_quality(self.cases, self.learned).to_dict(), range(40)))
        self.assertEqual(len({json.dumps(r, sort_keys=True) for r in results}), 1)

    def test_rollback_does_not_mutate_current(self):
        before = self.learned.to_dict()
        r = evaluate_quality([sample(i, "REVIEW_RETURN") for i in range(10)], self.learned)
        rollback_on_degradation(self.learned, self.previous, r)
        self.assertEqual(self.learned.to_dict(), before)

    def test_policy_blocks_learning_even_if_preferred(self):
        state = DecisionLearningState(gather_adjustment=0.08, gather_samples=4)
        r = AdvancedReasoner().rank({"march_available": 0}, verified=True,
                                   options=["WAIT", "REVIEW_GATHER"], learning_state=state)
        self.assertEqual(r.selected, "WAIT")

    def test_verified_outcome_updates_are_separate_from_holdout(self):
        learner = DecisionLearner()
        updated = learner.observe(self.previous, "REVIEW_GATHER", successful=True, verified=True)
        evaluate_quality(self.cases, updated)
        self.assertEqual(updated.gather_samples, 1)

if __name__ == "__main__":
    unittest.main()
