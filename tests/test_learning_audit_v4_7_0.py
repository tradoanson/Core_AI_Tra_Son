import unittest

from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.learning_audit_v1 import audit_learning_scenarios


def scenario(seed, factor=1.2):
    return [LearningExample(f"{seed}-{i}", f"{seed}-group-{i}",
                            "train" if i <= 10 else "test",
                            i * 10, i * 10 * factor, True)
            for i in range(1, 31)]


class LearningAuditV1Tests(unittest.TestCase):
    def test_multiple_improving_scenarios(self):
        result = audit_learning_scenarios([scenario(1), scenario(2, 1.1), scenario(3, 1.3)])
        self.assertTrue(result.accepted)
        self.assertGreater(result.improved_scenarios, 0)
        self.assertFalse(result.promoted)

    def test_baseline_only_is_not_success(self):
        result = audit_learning_scenarios([scenario(1, 1), scenario(2, 1), scenario(3, 1)])
        self.assertFalse(result.accepted)

    def test_duplicate_scenario_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit_learning_scenarios([scenario(1), scenario(1), scenario(2)])

    def test_too_few_scenarios_rejected(self):
        with self.assertRaises(ValueError):
            audit_learning_scenarios([scenario(1)])

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            audit_learning_scenarios([scenario(1)], min_scenarios=0)

    def test_unverified_label_rejected(self):
        rows = scenario(1)
        rows[0] = LearningExample("1-1", "1-group-1", "train", 10, 12, False)
        with self.assertRaises(ValueError):
            audit_learning_scenarios([rows, scenario(2), scenario(3)])

    def test_deterministic_order(self):
        a = [scenario(1), scenario(2, 1.1), scenario(3, 1.3)]
        self.assertEqual(audit_learning_scenarios(a), audit_learning_scenarios(list(reversed(a))))

    def test_does_not_mutate_scenarios(self):
        rows = [scenario(1), scenario(2), scenario(3)]
        original = [list(x) for x in rows]
        audit_learning_scenarios(rows)
        self.assertEqual(rows, original)

    def test_empty_test_rejected(self):
        rows = scenario(1)[:10]
        with self.assertRaises(ValueError):
            audit_learning_scenarios([rows, scenario(2), scenario(3)])

    def test_no_promotion(self):
        self.assertIs(audit_learning_scenarios([scenario(1), scenario(2), scenario(3)]).promoted, False)


if __name__ == "__main__":
    unittest.main()
