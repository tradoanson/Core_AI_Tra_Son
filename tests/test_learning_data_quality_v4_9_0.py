import unittest
from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.learning_data_quality_v1 import evaluate_learning_data_quality


def dataset():
    return [LearningExample(str(i), f"g{i}", "train", 100, 110, True)
            for i in range(1, 21)]


class DataQualityTests(unittest.TestCase):
    def test_clean_passes(self):
        self.assertTrue(evaluate_learning_data_quality(dataset()).accepted)
    def test_single_anomaly_within_budget(self):
        rows = dataset()
        rows[0] = LearningExample("1", "g1", "train", 100, 1000, True)
        r = evaluate_learning_data_quality(rows)
        self.assertEqual(r.anomaly_count, 1)
        self.assertTrue(r.accepted)
    def test_excessive_anomalies_rejected(self):
        rows = dataset()
        for i in range(4):
            rows[i] = LearningExample(str(i + 1), f"g{i+1}", "train", 100, 1000, True)
        self.assertFalse(evaluate_learning_data_quality(rows).accepted)
    def test_insufficient_samples(self):
        self.assertEqual(evaluate_learning_data_quality(dataset()[:3]).reason,
                         "insufficient_training_samples")
    def test_invalid_policy(self):
        with self.assertRaises(ValueError):
            evaluate_learning_data_quality(dataset(), max_anomaly_fraction=2)
    def test_nan_policy(self):
        with self.assertRaises(ValueError):
            evaluate_learning_data_quality(dataset(), max_absolute_error_seconds=float("nan"))
    def test_unverified_rejected(self):
        rows = dataset()
        rows[0] = LearningExample("1", "g1", "train", 100, 110, False)
        with self.assertRaises(ValueError):
            evaluate_learning_data_quality(rows)
    def test_order_independent(self):
        self.assertEqual(evaluate_learning_data_quality(dataset()),
                         evaluate_learning_data_quality(list(reversed(dataset()))))
    def test_input_unchanged(self):
        rows = dataset()
        before = list(rows)
        evaluate_learning_data_quality(rows)
        self.assertEqual(rows, before)
    def test_zero_anomalies(self):
        self.assertEqual(evaluate_learning_data_quality(dataset()).anomaly_fraction, 0)

if __name__ == "__main__":
    unittest.main()
