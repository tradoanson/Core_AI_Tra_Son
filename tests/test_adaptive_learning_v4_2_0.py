import unittest

from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.adaptive_learning_v3 import (
    AdaptiveModelV3, evaluate_adaptive_v3, train_adaptive_v3
)


def row(name, group, split, pred, actual, verified=True):
    return LearningExample(name, group, split, pred, actual, verified)


def dataset():
    return [row("train1", "g1", "train", 100, 120),
            row("train2", "g2", "train", 200, 220),
            row("test1", "g3", "test", 300, 320),
            row("test2", "g4", "test", 400, 420)]


class AdaptiveV3Tests(unittest.TestCase):
    def test_training_improves_holdout(self):
        rows = dataset()
        model = train_adaptive_v3(rows, epochs=4)
        result = evaluate_adaptive_v3(rows, model)
        self.assertLess(result["adaptive_mae_seconds"], result["baseline_mae_seconds"])
        self.assertFalse(result["promoted"])

    def test_training_ignores_test_labels(self):
        a = dataset()
        b = dataset()
        b[-1] = row("test2", "g4", "test", 400, 999)
        self.assertEqual(train_adaptive_v3(a), train_adaptive_v3(b))

    def test_deterministic_order(self):
        self.assertEqual(train_adaptive_v3(dataset()), train_adaptive_v3(list(reversed(dataset()))))

    def test_unverified_rejected(self):
        rows = dataset()
        rows[0] = row("train1", "g1", "train", 100, 120, False)
        with self.assertRaises(ValueError):
            train_adaptive_v3(rows)

    def test_empty_train_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty training"):
            train_adaptive_v3([row("test", "g", "test", 100, 120)])

    def test_epochs_bounded(self):
        with self.assertRaises(ValueError):
            train_adaptive_v3(dataset(), epochs=11)

    def test_bias_bounded(self):
        rows = [row("a", "g1", "train", 0, 604800)]
        self.assertLessEqual(abs(train_adaptive_v3(rows, epochs=10).bias_seconds), 300)

    def test_invalid_model_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_adaptive_v3(dataset(), AdaptiveModelV3(float("nan")))

    def test_no_dataset_mutation(self):
        rows = dataset()
        before = list(rows)
        train_adaptive_v3(rows)
        self.assertEqual(rows, before)

    def test_no_automatic_promotion(self):
        self.assertIs(evaluate_adaptive_v3(dataset(), train_adaptive_v3(dataset()))["promoted"], False)


if __name__ == "__main__":
    unittest.main()
