import unittest

from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.tiny_ml_v1 import TinyMLModelV1, train_tiny_ml_v1, predict_tiny_ml_v1, evaluate_tiny_ml_v1


def row(id, group, split, pred, actual, verified=True):
    return LearningExample(id, group, split, pred, actual, verified)


def dataset():
    return [row("a", "g1", "train", 100, 120),
            row("b", "g2", "train", 200, 240),
            row("c", "g3", "train", 300, 360),
            row("d", "g4", "test", 400, 480),
            row("e", "g5", "test", 500, 600)]


class TinyMLV1Tests(unittest.TestCase):
    def test_fit_improves_holdout(self):
        model = train_tiny_ml_v1(dataset())
        report = evaluate_tiny_ml_v1(dataset(), model)
        self.assertLess(report["tiny_ml_mae_seconds"], report["baseline_mae_seconds"])
        self.assertFalse(report["promoted"])

    def test_train_ignores_test_labels(self):
        a, b = dataset(), dataset()
        b[-1] = row("e", "g5", "test", 500, 999)
        self.assertEqual(train_tiny_ml_v1(a), train_tiny_ml_v1(b))

    def test_deterministic_order(self):
        self.assertEqual(train_tiny_ml_v1(dataset()), train_tiny_ml_v1(list(reversed(dataset()))))

    def test_unverified_rejected(self):
        rows = dataset()
        rows[0] = row("a", "g1", "train", 100, 120, False)
        with self.assertRaises(ValueError):
            train_tiny_ml_v1(rows)

    def test_insufficient_train_rejected(self):
        with self.assertRaises(ValueError):
            train_tiny_ml_v1([row("a", "g", "train", 1, 2)])

    def test_invalid_model_rejected(self):
        with self.assertRaises(ValueError):
            predict_tiny_ml_v1(TinyMLModelV1(float("nan"), 0, 2), 10)

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            predict_tiny_ml_v1(TinyMLModelV1(0, 0, 2), float("inf"))

    def test_clamps_negative_predictions(self):
        self.assertEqual(predict_tiny_ml_v1(TinyMLModelV1(-300, 0, 2), 10), 0)

    def test_no_dataset_mutation(self):
        rows = dataset()
        before = list(rows)
        train_tiny_ml_v1(rows)
        self.assertEqual(rows, before)

    def test_group_leakage_rejected(self):
        rows = dataset()
        rows[-1] = row("e", "g1", "test", 500, 600)
        with self.assertRaises(ValueError):
            train_tiny_ml_v1(rows)


if __name__ == "__main__":
    unittest.main()
