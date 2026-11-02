import unittest

from core_ai_tra_son.learning_foundation import (
    LearningExample, dataset_digest, evaluate_baseline, validate_dataset
)


def sample(id="a", group="g", split="test", pred=10, actual=12, verified=True):
    return LearningExample(id, group, split, pred, actual, verified)


class LearningFoundationTests(unittest.TestCase):
    def test_baseline_metrics(self):
        result = evaluate_baseline([sample(), sample("b", "h", pred=20, actual=24)])
        self.assertEqual(result["samples"], 2)
        self.assertEqual(result["mae_seconds"], 3)
        self.assertEqual(result["p95_absolute_error_seconds"], 4)

    def test_unverified_rejected(self):
        with self.assertRaisesRegex(ValueError, "unverified"):
            validate_dataset([sample(verified=False)])

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_dataset([sample(), sample(group="h")])

    def test_group_leakage_rejected(self):
        with self.assertRaisesRegex(ValueError, "leakage"):
            validate_dataset([sample(), sample("b", "g", "train")])

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            validate_dataset([sample(pred=float("nan"))])

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            validate_dataset([sample(actual=-1)])

    def test_empty_split_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            evaluate_baseline([sample(split="train")])

    def test_digest_order_independent(self):
        a, b = sample(), sample("b", "h")
        self.assertEqual(dataset_digest([a, b]), dataset_digest([b, a]))

    def test_no_mutation(self):
        rows = [sample()]
        before = list(rows)
        evaluate_baseline(rows)
        self.assertEqual(rows, before)

    def test_bool_is_not_eta(self):
        with self.assertRaises(ValueError):
            validate_dataset([sample(pred=True)])


if __name__ == "__main__":
    unittest.main()
