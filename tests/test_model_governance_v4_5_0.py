import unittest
from dataclasses import replace

from core_ai_tra_son.model_governance_v1 import (
    ModelQualityReport, evaluate_model_governance, choose_rollback
)


def report(**kw):
    data = dict(model_id="tiny-v1", dataset_sha256="a" * 64, samples=100,
                baseline_mae_seconds=100, candidate_mae_seconds=80,
                baseline_p95_seconds=200, candidate_p95_seconds=195)
    data.update(kw)
    return ModelQualityReport(**data)


class ModelGovernanceTests(unittest.TestCase):
    def test_accepts_improvement(self):
        d = evaluate_model_governance(report())
        self.assertTrue(d.accepted)
        self.assertEqual(d.selected_model_id, "tiny-v1")

    def test_rejects_insufficient_samples(self):
        self.assertEqual(evaluate_model_governance(report(samples=2)).reason, "insufficient_samples")

    def test_rejects_insufficient_improvement(self):
        self.assertEqual(evaluate_model_governance(report(candidate_mae_seconds=99)).reason, "insufficient_improvement")

    def test_rejects_tail_regression(self):
        self.assertEqual(evaluate_model_governance(report(candidate_p95_seconds=230)).reason, "tail_regression")

    def test_rejects_zero_baseline(self):
        self.assertEqual(evaluate_model_governance(report(baseline_mae_seconds=0)).reason, "zero_baseline_error")

    def test_rejects_nan(self):
        with self.assertRaises(ValueError):
            evaluate_model_governance(report(candidate_mae_seconds=float("nan")))

    def test_rejects_invalid_digest(self):
        with self.assertRaises(ValueError):
            evaluate_model_governance(report(dataset_sha256="bad"))

    def test_rollback_on_drift(self):
        d = choose_rollback("tiny-v1", "baseline", drift_detected=True)
        self.assertFalse(d.accepted)
        self.assertEqual(d.selected_model_id, "baseline")

    def test_keep_when_stable(self):
        self.assertEqual(choose_rollback("tiny-v1", "baseline").selected_model_id, "tiny-v1")

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_model_governance(report(), min_improvement_percent=-1)


if __name__ == "__main__":
    unittest.main()
