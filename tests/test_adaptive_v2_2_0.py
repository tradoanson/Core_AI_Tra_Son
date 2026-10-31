import unittest
from core_ai_tra_son.adaptive_v2 import advise_adaptation
class AdaptiveV2Tests(unittest.TestCase):
    def test_drift_freezes(self):self.assertEqual(advise_adaptation([True]*20,[False]*20).status,"FROZEN")
    def test_insufficient_freezes(self):self.assertEqual(advise_adaptation([True]*2,[True]*2).status,"FROZEN")
    def test_stable_requires_review(self):self.assertEqual(advise_adaptation([True]*20,[True]*20).status,"REVIEW_REQUIRED")
    def test_no_auto_learning(self):self.assertFalse(advise_adaptation([True]*20,[True]*20).learning_allowed)
    def test_no_action(self):self.assertFalse(advise_adaptation([True]*20,[True]*20).action_executed)
    def test_no_delta(self):self.assertEqual(advise_adaptation([True]*20,[True]*20).proposed_delta,0)
    def test_bad_step(self):
        with self.assertRaises(ValueError):advise_adaptation([True]*20,[True]*20,maximum_step=0.5)
    def test_bad_current(self):
        with self.assertRaises(ValueError):advise_adaptation([True]*20,[True]*20,current_delta=2)
