import unittest
from core_ai_tra_son.quality_gate import paired_quality_gate
from core_ai_tra_son.decision_quality import QualityReport, DecisionCase, evaluate_quality
from core_ai_tra_son.decision_learning import DecisionLearningState

def report(wins, losses, status="PASS"):
    return QualityReport(wins+losses,wins+losses,losses,wins,0,0,0,
                         tuple("loss"+str(i) for i in range(losses)),
                         tuple("win"+str(i) for i in range(wins)),(),status)

class QualityGateTests(unittest.TestCase):
    def test_strong_improvement(self):
        self.assertEqual(paired_quality_gate(report(10,0)).status,"PASS")
    def test_all_regressions(self):
        self.assertEqual(paired_quality_gate(report(0,10)).status,"DEGRADED")
    def test_equal_changes(self):
        self.assertEqual(paired_quality_gate(report(5,5)).status,"DEGRADED")
    def test_too_few_changes(self):
        self.assertEqual(paired_quality_gate(report(7,0)).status,"INSUFFICIENT_EVIDENCE")
    def test_no_changes(self):
        self.assertEqual(paired_quality_gate(report(0,0)).status,"INSUFFICIENT_EVIDENCE")
    def test_quality_failure_not_overridden(self):
        self.assertEqual(paired_quality_gate(report(10,0,"DEGRADED")).status,"DEGRADED")
    def test_missing_evidence(self):
        self.assertEqual(paired_quality_gate(report(10,0,"INSUFFICIENT_EVIDENCE")).status,"INSUFFICIENT_EVIDENCE")
    def test_bad_alpha(self):
        with self.assertRaises(ValueError): paired_quality_gate(report(10,0),alpha=0)
    def test_bad_sample(self):
        with self.assertRaises(ValueError): paired_quality_gate(report(10,0),minimum_discordant=0)
    def test_invalid_report(self):
        with self.assertRaises(ValueError): paired_quality_gate(None)
    def test_exact_p(self):
        self.assertAlmostEqual(paired_quality_gate(report(10,0)).exact_p_value,1/1024)
    def test_shadow(self):
        self.assertFalse(paired_quality_gate(report(10,0)).action_executed)
