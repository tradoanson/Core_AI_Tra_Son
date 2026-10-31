import unittest
from core_ai_tra_son.learning_drift import detect_outcome_drift as detect
class DriftTests(unittest.TestCase):
    def test_stable(self): self.assertEqual(detect([True]*20,[True]*20).status,"STABLE")
    def test_drift(self): self.assertEqual(detect([True]*20,[False]*20).status,"DRIFT")
    def test_pause(self): self.assertTrue(detect([True]*20,[False]*20).pause_recommended)
    def test_small_pauses(self): self.assertTrue(detect([True]*5,[False]*5).pause_recommended)
    def test_unverified_rejected(self):
        with self.assertRaises(ValueError): detect([1]*20,[False]*20)
    def test_large_rejected(self):
        with self.assertRaises(ValueError): detect([True]*513,[False]*20)
    def test_no_host_action(self): self.assertFalse(detect([True]*20,[False]*20).action_executed)
    def test_invalid_tolerance(self):
        with self.assertRaises(ValueError): detect([True]*20,[False]*20,tolerance=0)
