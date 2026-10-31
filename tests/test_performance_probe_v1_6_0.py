import unittest
from core_ai_tra_son.performance_probe import benchmark_shadow
class PerformanceTests(unittest.TestCase):
    def test_count(self):self.assertEqual(benchmark_shadow({"march_available":0},iterations=3).iterations,3)
    def test_positive(self):self.assertGreaterEqual(benchmark_shadow({"march_available":0},iterations=2).elapsed_ms,0)
    def test_no_action(self):self.assertFalse(benchmark_shadow({"march_available":0},iterations=2).action_executed)
    def test_bad_count(self):
        with self.assertRaises(ValueError):benchmark_shadow({},iterations=0)
    def test_bad_budget(self):
        with self.assertRaises(ValueError):benchmark_shadow({},budget_ms=0)
    def test_bad_signals(self):
        with self.assertRaises(ValueError):benchmark_shadow(None)
