import concurrent.futures
import json
import unittest
from core_ai_tra_son.decision_learning import DecisionLearner, DecisionLearningState, MAX_ADJUSTMENT
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner

class AdaptiveDecisionLearningTests(unittest.TestCase):
    def setUp(self):
        self.learner = DecisionLearner()
        self.ranker = AdvancedReasoner()
        self.signals = {"march_available": 2, "resource_available": True,
                        "eta_seconds": 100, "return_buffer_seconds": 300}
        self.options = ["WAIT", "REVIEW_GATHER", "REVIEW_RETURN"]

    def test_unverified_outcome_no_learning(self):
        state = DecisionLearningState()
        self.assertIs(self.learner.observe(state, "REVIEW_GATHER", successful=True), state)

    def test_verified_positive_and_negative(self):
        a = self.learner.observe(DecisionLearningState(), "REVIEW_GATHER", successful=True, verified=True)
        b = self.learner.observe(a, "REVIEW_GATHER", successful=False, verified=True)
        self.assertEqual(a.gather_adjustment, 0.02)
        self.assertEqual(b.gather_adjustment, 0)
        self.assertEqual(b.gather_samples, 2)

    def test_saturates_with_bounded_bias(self):
        state = DecisionLearningState()
        for _ in range(100):
            state = self.learner.observe(state, "REVIEW_RETURN", successful=True, verified=True)
        self.assertEqual(state.return_adjustment, MAX_ADJUSTMENT)

    def test_negative_saturation(self):
        state = DecisionLearningState()
        for _ in range(100):
            state = self.learner.observe(state, "REVIEW_GATHER", successful=False, verified=True)
        self.assertEqual(state.gather_adjustment, -MAX_ADJUSTMENT)

    def test_wait_cannot_learn(self):
        with self.assertRaises(ValueError):
            self.learner.observe(DecisionLearningState(), "WAIT", successful=True, verified=True)

    def test_non_boolean_outcome_rejected(self):
        with self.assertRaises(ValueError):
            self.learner.observe(DecisionLearningState(), "REVIEW_GATHER", successful=1, verified=True)

    def test_invalid_learning_state_fails_closed(self):
        bad = DecisionLearningState(gather_adjustment=100)
        self.assertEqual(self.ranker.rank(self.signals, verified=True,
                          options=self.options, learning_state=bad).status, "UNRESOLVED")

    def test_learning_can_change_ranking(self):
        # Base: return due (0.75) outranks gather (0.65).
        state = DecisionLearningState()
        for _ in range(4):
            state = self.learner.observe(state, "REVIEW_GATHER", successful=True, verified=True)
            state = self.learner.observe(state, "REVIEW_RETURN", successful=False, verified=True)
        baseline = self.ranker.rank(self.signals, verified=True, options=self.options)
        adapted = self.ranker.rank(self.signals, verified=True, options=self.options, learning_state=state)
        self.assertEqual(baseline.selected, "REVIEW_RETURN")
        self.assertEqual(adapted.selected, "REVIEW_GATHER")
        self.assertEqual(baseline.confidence, adapted.confidence)

    def test_learning_never_unblocks_gather(self):
        state = DecisionLearningState(gather_adjustment=0.08, gather_samples=4)
        r = self.ranker.rank({"march_available": 2}, verified=True,
                             options=["WAIT", "REVIEW_GATHER"], learning_state=state)
        self.assertEqual(r.selected, "WAIT")
        self.assertEqual(next(x for x in r.alternatives if x.option == "REVIEW_GATHER").score, 0)

    def test_learning_never_unblocks_return(self):
        state = DecisionLearningState(return_adjustment=0.08, return_samples=4)
        r = self.ranker.rank({"march_available": 2}, verified=True,
                             options=["WAIT", "REVIEW_RETURN"], learning_state=state)
        self.assertEqual(r.selected, "WAIT")

    def test_learning_never_overrides_conflict(self):
        r = self.ranker.rank({"march_available": 3, "march_capacity": 2},
                             verified=True, options=self.options, learning_state=DecisionLearningState())
        self.assertEqual(r.status, "UNRESOLVED")

    def test_learning_never_overrides_unverified(self):
        r = self.ranker.rank(self.signals, verified=False,
                             options=self.options, learning_state=DecisionLearningState())
        self.assertEqual(r.status, "UNRESOLVED")

    def test_learning_does_not_change_wait_score(self):
        state = DecisionLearningState(gather_adjustment=0.08, return_adjustment=-0.08)
        a = self.ranker.rank(self.signals, verified=True, options=self.options)
        b = self.ranker.rank(self.signals, verified=True, options=self.options, learning_state=state)
        wait = lambda r: next(x.score for x in r.alternatives if x.option == "WAIT")
        self.assertEqual(wait(a), wait(b))

    def test_immutable_input_state(self):
        state = DecisionLearningState()
        updated = self.learner.observe(state, "REVIEW_GATHER", successful=True, verified=True)
        self.assertEqual(state.gather_samples, 0)
        self.assertEqual(updated.gather_samples, 1)

    def test_reject_nonfinite_and_foreign_state(self):
        for state in (DecisionLearningState(gather_adjustment=float("nan")),
                      DecisionLearningState(namespace="nhankhau"),
                      DecisionLearningState(return_samples=True)):
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.learner.observe(state, "REVIEW_RETURN", successful=True, verified=True)

    def test_sample_limit(self):
        state = DecisionLearningState(gather_samples=1000000)
        self.assertIs(self.learner.observe(state, "REVIEW_GATHER", successful=True, verified=True), state)

    def test_parallel_determinism(self):
        state = DecisionLearningState(gather_adjustment=0.04, return_adjustment=-0.02)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda _: self.ranker.rank(
                self.signals, verified=True, options=self.options, learning_state=state).to_dict(), range(100)))
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in outputs}), 1)

    def test_no_action_execution(self):
        r = self.ranker.rank(self.signals, verified=True,
                             options=self.options, learning_state=DecisionLearningState())
        self.assertFalse(r.action_executed)

    def test_serializable_state(self):
        json.dumps(DecisionLearningState().to_dict())

if __name__ == "__main__":
    unittest.main()
