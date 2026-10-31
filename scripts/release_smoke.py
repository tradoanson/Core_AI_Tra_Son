"""Offline smoke test for the installed Core AI Trà Sơn package."""
import json
from importlib.metadata import version
from core_ai_tra_son import CoreAI
from core_ai_tra_son.adaptive import EtaAdaptive
from core_ai_tra_son.tiny_ai import TinyPredictor

assert version("core-ai-tra-son") == "0.4.1"
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
