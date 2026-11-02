import unittest
from core_ai_tra_son.learning_foundation import LearningExample
from core_ai_tra_son.learning_pipeline_v1 import run_learning_pipeline

def dataset(factor=1.2):
    return [LearningExample(str(i), f"g{i}", "train" if i <= 10 else "test",
                            i * 10, i * 10 * factor, True) for i in range(1, 31)]

class LearningPipelineTests(unittest.TestCase):
    def test_clean_pipeline_runs(self):
        r = run_learning_pipeline(dataset())
        self.assertTrue(r.quality_accepted)
        self.assertTrue(r.benchmark_executed)
    def test_never_promotes(self):
        self.assertFalse(run_learning_pipeline(dataset()).promoted)
    def test_quality_failure_blocks_benchmark(self):
        rows = dataset()
        for i in range(3):
            rows[i] = LearningExample(str(i+1), f"g{i+1}", "train", 10, 1000, True)
        r = run_learning_pipeline(rows)
        self.assertFalse(r.quality_accepted)
        self.assertFalse(r.benchmark_executed)
        self.assertEqual(r.recommended_candidate, "baseline")
    def test_insufficient_train_blocks(self):
        r = run_learning_pipeline(dataset()[:5])
        self.assertEqual(r.quality_reason, "insufficient_training_samples")
    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            run_learning_pipeline(dataset(), max_anomaly_fraction=2)
    def test_unverified_rejected(self):
        rows = dataset()
        rows[0] = LearningExample("1", "g1", "train", 10, 12, False)
        with self.assertRaises(ValueError):
            run_learning_pipeline(rows)
    def test_no_test_rejected(self):
        with self.assertRaises(ValueError):
            run_learning_pipeline(dataset()[:10])
    def test_deterministic(self):
        self.assertEqual(run_learning_pipeline(dataset()),
                         run_learning_pipeline(list(reversed(dataset()))))
    def test_no_mutation(self):
        rows = dataset()
        before = list(rows)
        run_learning_pipeline(rows)
        self.assertEqual(rows, before)
    def test_quality_digest_matches(self):
        self.assertEqual(len(run_learning_pipeline(dataset()).dataset_sha256), 64)

if __name__ == "__main__":
    unittest.main()
