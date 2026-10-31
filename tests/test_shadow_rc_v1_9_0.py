"""Offline release-candidate integration regression across independent gates."""
import unittest
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner
from core_ai_tra_son.decision_explanation import explain_ranking
from core_ai_tra_son.learning_drift import detect_outcome_drift
from core_ai_tra_son.holdout_leakage import audit_holdout_leakage
from core_ai_tra_son.decision_quality import DecisionCase
from core_ai_tra_son.recovery_audit import RecoveryAudit
from core_ai_tra_son.recovery_anchor import issue_anchor,verify_anchor
from core_ai_tra_son.release_readiness import evaluate_readiness
from core_ai_tra_son.quality_gate import QualityGate
from core_ai_tra_son.decision_learning import DecisionLearningState
from core_ai_tra_son.shadow_adapter import shadow_adapter

class ReleaseCandidateTests(unittest.TestCase):
    def test_safe_wait_and_explanation(self):
        r=AdvancedReasoner().rank({"march_available":0},verified=True,options=["WAIT","REVIEW_GATHER"])
        self.assertEqual(explain_ranking(r).selected,"WAIT")
        self.assertFalse(r.action_executed)
    def test_unverified_adapter_rejects(self):
        self.assertEqual(shadow_adapter({"march_available":2}).status,"UNRESOLVED")
    def test_split_audit(self):
        a=[DecisionCase("a"+str(i),{"march_available":i},"WAIT") for i in range(8)]
        b=[DecisionCase("b"+str(i),{"march_available":i+100},"WAIT") for i in range(8)]
        self.assertEqual(audit_holdout_leakage(a,b).status,"PASS")
    def test_drift_pause(self):
        self.assertTrue(detect_outcome_drift([True]*20,[False]*20).pause_recommended)
    def test_recovery_anchor(self):
        audit=RecoveryAudit(b"a"*32)
        entries=audit.append((),target="REVIEWED",reviewer="reviewer",evidence=b"proof",evidence_valid=True,independent_reviewer=True)
        anchor=issue_anchor(audit,entries,anchor_key=b"b"*32)
        self.assertTrue(verify_anchor(audit,entries,anchor,anchor_key=b"b"*32))
    def test_readiness_never_authorizes_production(self):
        result=evaluate_readiness(quality=QualityGate("PASS",10,0,10,0.001),audit=RecoveryAudit(b"k"*32),
            entries=(),recovered_state=DecisionLearningState(),provenance_verified=True,
            integrity_verified=True,human_reviewed=True)
        self.assertEqual(result.status,"PASS")
        self.assertFalse(result.production_approved)
        self.assertFalse(result.action_executed)
