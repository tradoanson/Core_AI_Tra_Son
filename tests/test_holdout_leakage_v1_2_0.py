import unittest
from core_ai_tra_son.decision_quality import DecisionCase
from core_ai_tra_son.holdout_leakage import audit_holdout_leakage

def case(prefix,i,verified=True):
    return DecisionCase(prefix+str(i),{"march_available":i,"eta_seconds":i*10},"WAIT",verified=verified)

class LeakageTests(unittest.TestCase):
    def setUp(self):
        self.training=[case("train",i) for i in range(8)]
        self.holdout=[case("hold",i+100) for i in range(8)]
    def test_clean(self):
        self.assertEqual(audit_holdout_leakage(self.training,self.holdout).status,"PASS")
    def test_cross_duplicate(self):
        self.holdout[0]=case("hold",0)
        r=audit_holdout_leakage(self.training,self.holdout)
        self.assertEqual(r.status,"BLOCKED")
        self.assertEqual(r.cross_split_duplicates,1)
    def test_duplicate_training(self):
        self.training[1]=case("train1",0)
        self.assertEqual(audit_holdout_leakage(self.training,self.holdout).status,"BLOCKED")
    def test_duplicate_holdout(self):
        self.holdout[1]=case("hold1",100)
        self.assertEqual(audit_holdout_leakage(self.training,self.holdout).status,"BLOCKED")
    def test_overlap_id(self):
        self.holdout[0]=case("train",0)
        with self.assertRaises(ValueError): audit_holdout_leakage(self.training,self.holdout)
    def test_unverified(self):
        self.holdout[0]=case("hold",100,False)
        with self.assertRaises(ValueError): audit_holdout_leakage(self.training,self.holdout)
    def test_small(self):
        with self.assertRaises(ValueError): audit_holdout_leakage(self.training[:7],self.holdout)
    def test_no_action(self):
        self.assertFalse(audit_holdout_leakage(self.training,self.holdout).action_executed)
