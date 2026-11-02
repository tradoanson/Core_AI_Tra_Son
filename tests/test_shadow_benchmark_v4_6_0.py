import unittest

from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.shadow_benchmark_v1 import run_shadow_benchmark


def row(i, split, pred, actual, verified=True):
    return LearningExample(str(i), "group-" + str(i), split, pred, actual, verified)


def dataset():
    return [row(i, "train", i * 10, i * 12) for i in range(1, 11)] + [
        row(i, "test", i * 10, i * 12) for i in range(11, 31)]


class ShadowBenchmarkV1Tests(unittest.TestCase):
    def test_benchmark_runs(self):
        result = run_shadow_benchmark(dataset())
        self.assertEqual(result.train_samples, 10)
        self.assertEqual(result.test_samples, 20)

    def test_tiny_improves(self):
        result = run_shadow_benchmark(dataset())
        self.assertLess(result.tiny_ml_mae_seconds, result.baseline_mae_seconds)

    def test_no_promotion(self):
        self.assertFalse(run_shadow_benchmark(dataset()).promoted)

    def test_reproducible_order(self):
        self.assertEqual(run_shadow_benchmark(dataset()), run_shadow_benchmark(list(reversed(dataset()))))

    def test_unverified_rejected(self):
        rows = dataset()
        rows[0] = row(1, "train", 10, 12, False)
        with self.assertRaises(ValueError):
            run_shadow_benchmark(rows)

    def test_insufficient_test_rejected(self):
        with self.assertRaises(ValueError):
            run_shadow_benchmark(dataset()[:12])

    def test_insufficient_train_rejected(self):
        with self.assertRaises(ValueError):
            run_shadow_benchmark([row(1, "train", 10, 12)] + dataset()[10:])

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            run_shadow_benchmark(dataset(), min_test_samples=0)

    def test_dataset_not_mutated(self):
        rows = dataset()
        before = list(rows)
        run_shadow_benchmark(rows)
        self.assertEqual(rows, before)

    def test_group_leakage_rejected(self):
        rows = dataset()
        rows[-1] = LearningExample("30", "group-1", "test", 300, 360, True)
        with self.assertRaises(ValueError):
            run_shadow_benchmark(rows)


if __name__ == "__main__":
    unittest.main()
