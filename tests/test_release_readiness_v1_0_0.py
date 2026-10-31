import unittest
from core_ai_tra_son.release_readiness import evaluate_readiness
from core_ai_tra_son.quality_gate import QualityGate
from core_ai_tra_son.recovery_audit import RecoveryAudit
from core_ai_tra_son.decision_learning import DecisionLearningState

class ReleaseReadinessTests(unittest.TestCase):
    def setUp(self):
        self.audit=RecoveryAudit(b"k"*32)
        self.quality=QualityGate("PASS",10,0,10,0.0009765625)
        self.args=dict(quality=self.quality,audit=self.audit,entries=(),
            recovered_state=DecisionLearningState(),provenance_verified=True,
            integrity_verified=True,human_reviewed=True,shadow_only=True)
    def test_pass(self):
        self.assertEqual(evaluate_readiness(**self.args).status,"PASS")
    def test_no_action(self):
        self.assertFalse(evaluate_readiness(**self.args).action_executed)
    def test_never_production(self):
        self.assertFalse(evaluate_readiness(**self.args).production_approved)
    def test_block_quality(self):
        self.args["quality"]=QualityGate("DEGRADED",0,10,10,1.0)
        self.assertEqual(evaluate_readiness(**self.args).status,"BLOCKED")
    def test_block_insufficient(self):
        self.args["quality"]=QualityGate("INSUFFICIENT_EVIDENCE",0,0,0,1.0)
        self.assertEqual(evaluate_readiness(**self.args).status,"BLOCKED")
    def test_block_quality_action(self):
        self.args["quality"]=QualityGate("PASS",10,0,10,0.001,action_executed=True)
        self.assertEqual(evaluate_readiness(**self.args).status,"BLOCKED")
    def test_block_low_discordant(self):
        self.args["quality"]=QualityGate("PASS",7,0,7,0.01)
        self.assertEqual(evaluate_readiness(**self.args).status,"BLOCKED")
    def test_block_provenance(self):
        self.args["provenance_verified"]=False
        self.assertIn("provenance_not_verified",evaluate_readiness(**self.args).reasons)
    def test_block_integrity(self):
        self.args["integrity_verified"]=False
        self.assertIn("integrity_not_verified",evaluate_readiness(**self.args).reasons)
    def test_block_review(self):
        self.args["human_reviewed"]=False
        self.assertIn("independent_review_missing",evaluate_readiness(**self.args).reasons)
    def test_block_shadow(self):
        self.args["shadow_only"]=False
        self.assertIn("shadow_boundary_required",evaluate_readiness(**self.args).reasons)
    def test_block_active_recovery(self):
        e=self.audit.append((),target="REVIEWED",reviewer="reviewer",evidence=b"proof",
            evidence_valid=True,independent_reviewer=True)
        self.args["entries"]=e
        self.assertIn("unresolved_recovery_lifecycle",evaluate_readiness(**self.args).reasons)
    def test_tampered_audit(self):
        e=self.audit.append((),target="REVIEWED",reviewer="reviewer",evidence=b"proof",
            evidence_valid=True,independent_reviewer=True)
        self.args["entries"]=e[::-1]+e
        with self.assertRaises(ValueError): evaluate_readiness(**self.args)
    def test_invalid_quality(self):
        self.args["quality"]=None
        with self.assertRaises(ValueError): evaluate_readiness(**self.args)
    def test_invalid_audit(self):
        self.args["audit"]=None
        with self.assertRaises(ValueError): evaluate_readiness(**self.args)
    def test_empty_reasons_on_pass(self):
        self.assertEqual(evaluate_readiness(**self.args).reasons,())
