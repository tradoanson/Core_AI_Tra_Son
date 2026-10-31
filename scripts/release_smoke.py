"""Offline smoke test for the installed Core AI Trà Sơn package."""
import json
from importlib.metadata import version
from core_ai_tra_son import CoreAI
from core_ai_tra_son.adaptive import EtaAdaptive
from core_ai_tra_son.tiny_ai import TinyPredictor

assert version("core-ai-tra-son") == "0.8.0"
assert CoreAI("vtnd").evaluate({"march_available": 0, "verified": True}).status == "WAITING"
assert CoreAI("vtnd").evaluate({"march_available": 1, "verified": False}).status == "UNRESOLVED"
assert CoreAI("nhankhau").evaluate({"record": {"name": "Sample"}, "required_fields": ["name", "birth_date"]}).details["missing_fields"] == ["birth_date"]
a = EtaAdaptive()
assert not a.observe(60, 80, verified=False)
assert a.observe(60, 80, verified=True)
assert a.correct(60) > 60
assert TinyPredictor().predict_eta(60, 5)["eta_seconds"] == 65
print(json.dumps({"version": version("core-ai-tra-son"), "offline_smoke": "PASS", "production_integrated": False}))

from core_ai_tra_son.validation import BenchmarkCase, validate_benchmark
assert validate_benchmark([BenchmarkCase("conflict", {"march_available": 2, "march_capacity": 1}, True, "UNRESOLVED")]).agreement == 1.0

from core_ai_tra_son.advanced_reasoning import AdvancedReasoner
ranking = AdvancedReasoner().rank({"march_available": 0}, verified=True, options=["WAIT", "REVIEW_GATHER"])
assert ranking.selected == "WAIT" and ranking.action_executed is False

quality = AdvancedReasoner().rank({"march_available": 2}, verified=True, options=["WAIT", "REVIEW_GATHER"])
assert quality.selected == "WAIT" and quality.action_executed is False

from core_ai_tra_son.decision_learning import DecisionLearner, DecisionLearningState
learner = DecisionLearner()
original = DecisionLearningState()
assert learner.observe(original, "REVIEW_GATHER", successful=True, verified=False) is original
learned = learner.observe(original, "REVIEW_GATHER", successful=True, verified=True)
assert learned.gather_adjustment > 0 and original.gather_adjustment == 0
shadow = AdvancedReasoner().rank({"march_available": 0}, verified=True, options=["WAIT", "REVIEW_GATHER"], learning_state=learned)
assert shadow.selected == "WAIT" and shadow.action_executed is False

import tempfile
from pathlib import Path
from core_ai_tra_son.learning_store import LearningStore
with tempfile.TemporaryDirectory() as directory:
    ledger = LearningStore(Path(directory) / "shadow.sqlite3")
    ledger.initialize()
    assert ledger.observe("smoke1", "REVIEW_GATHER", successful=True, verified=True)
    assert not ledger.observe("smoke1", "REVIEW_GATHER", successful=True, verified=True)
    assert ledger.state().gather_samples == 1

from core_ai_tra_son.secure_learning import SecureLearningStore
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    secured = SecureLearningStore(root / "secured.sqlite3", root / "checkpoint.json", b"k" * 32)
    secured.initialize()
    secured.bootstrap()
    assert secured.observe("smoke1", "REVIEW_GATHER", successful=True, verified=True)
    assert secured.state().gather_samples == 1
    assert not secured.observe("smoke1", "REVIEW_GATHER", successful=True, verified=True)

from core_ai_tra_son.hardened_learning import HardenedLearningStore
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    store = HardenedLearningStore(root / "ledger.sqlite3", root / "anchor.json", b"k" * 32)
    store.initialize()
    store.bootstrap()
    assert store.observe("smoke-1", "REVIEW_GATHER", successful=True, verified=True)
    assert not store.observe("smoke-1", "REVIEW_GATHER", successful=True, verified=True)
    assert store.state().gather_samples == 1

from core_ai_tra_son.decision_quality import DecisionCase, evaluate_quality, rollback_on_degradation
cases = [DecisionCase("smoke" + str(i), {"march_available": 2, "resource_available": True, "eta_seconds": 100, "return_buffer_seconds": 300}, "REVIEW_GATHER") for i in range(8)]
learned = DecisionLearningState(gather_adjustment=0.08, return_adjustment=-0.08, gather_samples=4, return_samples=4)
report = evaluate_quality(cases, learned)
assert report.status == "PASS" and report.delta > 0 and not report.action_executed
bad_cases = [DecisionCase("bad" + str(i), cases[i].signals, "REVIEW_RETURN") for i in range(8)]
bad = evaluate_quality(bad_cases, learned)
assert bad.status == "DEGRADED"
assert rollback_on_degradation(learned, DecisionLearningState(), bad) == DecisionLearningState()

from core_ai_tra_son.evaluation_integrity import EvaluationIntegrityStore
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    store = EvaluationIntegrityStore(root/"ledger.sqlite3", root/"anchor.json", b"k"*32,
                                     root/"evaluation.json", root/"rollback.json")
    store.initialize()
    store.bootstrap()
    for i in range(4):
        store.observe("train_g"+str(i), "REVIEW_GATHER", successful=True, verified=True)
        store.observe("train_r"+str(i), "REVIEW_RETURN", successful=False, verified=True)
    holdout = [DecisionCase("holdout"+str(i), {"march_available":2, "resource_available":True,
               "eta_seconds":100, "return_buffer_seconds":300}, "REVIEW_RETURN") for i in range(8)]
    assert store.evaluate_holdout(holdout).status == "DEGRADED"
    assert store.verify_evaluation()["report"]["status"] == "DEGRADED"
    store.activate_rollback(DecisionLearningState())
    assert store.effective_state() == DecisionLearningState()

from core_ai_tra_son.trusted_evaluation import TrustedEvaluationStore, issue_provenance, approve_rollback
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    trusted = TrustedEvaluationStore(root/"ledger.sqlite3", root/"anchor.json", b"l"*32,
                  root/"evaluation.json", root/"rollback.json", issuer_key=b"i"*32, approver_key=b"a"*32)
    trusted.initialize()
    trusted.bootstrap()
    for i in range(4):
        trusted.observe("train_g"+str(i), "REVIEW_GATHER", successful=True, verified=True)
        trusted.observe("train_r"+str(i), "REVIEW_RETURN", successful=False, verified=True)
    cases = [DecisionCase("holdout"+str(i), {"march_available":2, "resource_available":True,
            "eta_seconds":100, "return_buffer_seconds":300}, "REVIEW_RETURN") for i in range(8)]
    proof = issue_provenance(cases, issuer_id="external-issuer", issuer_key=b"i"*32)
    assert trusted.evaluate_trusted(cases, proof).status == "DEGRADED"
    request = trusted.rollback_request(0)
    approval = approve_rollback(request, approver_id="external-approver", approver_key=b"a"*32)
    assert trusted.activate_trusted_rollback(request, approval) == DecisionLearningState()
    assert trusted.effective_state() == DecisionLearningState()

from core_ai_tra_son.recovery_governance import RecoveryGovernance
assert RecoveryGovernance.transition("PROPOSED","REVIEWED",evidence_valid=True,independent_reviewer=True).eligible
assert not RecoveryGovernance.learning_allowed("CLOSED")

from core_ai_tra_son.recovery_audit import RecoveryAudit
signed = RecoveryAudit(b"k"*32)
entries = signed.append((),target="REVIEWED",reviewer="reviewer",evidence=b"proof",evidence_valid=True,independent_reviewer=True)
assert signed.verify(entries) == "REVIEWED"
