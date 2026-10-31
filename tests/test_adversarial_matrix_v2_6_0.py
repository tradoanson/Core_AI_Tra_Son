import unittest
from core_ai_tra_son.adversarial_matrix import run_adversarial_matrix
class AdversarialMatrixTests(unittest.TestCase):
    def test_matrix_pass(self):self.assertEqual(run_adversarial_matrix().status,"PASS")
    def test_case_count(self):self.assertEqual(run_adversarial_matrix().total,9)
    def test_all_pass(self):self.assertEqual(run_adversarial_matrix().passed,9)
    def test_no_failures(self):self.assertFalse(run_adversarial_matrix().failed_cases)
    def test_no_actions(self):self.assertFalse(run_adversarial_matrix().action_executed)
