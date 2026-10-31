"""Offline smoke test for the installed Core AI Trà Sơn package."""
import json
from importlib.metadata import version
from core_ai_tra_son import CoreAI
from core_ai_tra_son.adaptive import EtaAdaptive
from core_ai_tra_son.tiny_ai import TinyPredictor

assert version("core-ai-tra-son") == "0.6.3"
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
