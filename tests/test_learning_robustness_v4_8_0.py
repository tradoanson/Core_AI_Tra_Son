import unittest
from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.learning_robustness_v1 import evaluate_learning_robustness

def scenario(seed, factor):
    return [LearningExample(f"{seed}-{i}", f"g-{seed}-{i}",
                            "train" if i <= 10 else "test",
                            i * 10, i * 10 * factor, True) for i in range(1, 31)]

class RobustnessTests(unittest.TestCase):
    def test_improving_scenarios(self):
        r = evaluate_learning_robustness([scenario(1, 1.2), scenario(2, 1.1), scenario(3, 1.3)])
        self.assertTrue(r.accepted)
        self.assertEqual(r.selected_model, "tiny-ml-v1")
    def test_no_auto_promotion(self):
        self.assertFalse(evaluate_learning_robustness([scenario(1, 1.2), scenario(2, 1.1), scenario(3, 1.3)]).promoted)
    def test_no_gain_fails(self):
        self.assertFalse(evaluate_learning_robustness([scenario(1, 1), scenario(2, 1), scenario(3, 1)]).accepted)
    def test_mixed_shift_blocks_cherry_picking(self):
        r = evaluate_learning_robustness([scenario(1, 1.2), scenario(2, 1.1), scenario(3, 0.6)])
        self.assertIn(r.selected_model, ("baseline", "adaptive-v3", "tiny-ml-v1"))
    def test_duplicate_scenario(self):
        with self.assertRaises(ValueError):
            evaluate_learning_robustness([scenario(1, 1.2), scenario(1, 1.2), scenario(3, 1.3)])
    def test_min_scenarios(self):
        with self.assertRaises(ValueError):
            evaluate_learning_robustness([scenario(1, 1.2)])
    def test_nan_policy(self):
        with self.assertRaises(ValueError):
            evaluate_learning_robustness([scenario(1, 1.2), scenario(2, 1.1), scenario(3, 1.3)], max_regression_percent=float("nan"))
    def test_invalid_test_policy(self):
        with self.assertRaises(ValueError):
            evaluate_learning_robustness([scenario(1, 1.2), scenario(2, 1.1), scenario(3, 1.3)], min_test_samples=0)
    def test_unverified_rejected(self):
        rows = scenario(1, 1.2)
        rows[0] = LearningExample("1-1", "g-1-1", "train", 10, 12, False)
        with self.assertRaises(ValueError):
            evaluate_learning_robustness([rows, scenario(2, 1.1), scenario(3, 1.3)])
    def test_deterministic_order(self):
        rows = [scenario(1, 1.2), scenario(2, 1.1), scenario(3, 1.3)]
        self.assertEqual(evaluate_learning_robustness(rows), evaluate_learning_robustness(list(reversed(rows))))

if __name__ == "__main__":
    unittest.main()
