"""Pure SHADOW micro-agent: no host actions, no network, no persistent writes."""
from dataclasses import dataclass, asdict
from typing import Any
import math
from .engine import CoreAI

ALLOWED_PROFILES = frozenset({"vtnd", "nhankhau"})
ALLOWED_STATUSES = frozenset({"UNRESOLVED", "WAITING", "REVIEW", "PASS"})

@dataclass(frozen=True)
class AgentResult:
    profile: str
    status: str
    suggestion: str
    confidence: float
    reason_codes: tuple[str, ...]
    details: dict[str, Any]
    memory_used: bool
    action_executed: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["reason_codes"] = list(self.reason_codes)
        return result


class MicroAgent:
    """Observer -> optional memory context -> reasoner -> safety gate -> result.

    The caller may provide a previously read memory state. The agent itself
    never opens databases or invokes host application APIs.
    """
    def __init__(self, profile: str):
        if profile not in ALLOWED_PROFILES:
            raise ValueError("Unsupported profile")
        self.profile = profile
        self.reasoner = CoreAI(profile)

    def evaluate(self, observation: dict[str, Any], *, memory_state: dict[str, Any] | None = None) -> AgentResult:
        if not isinstance(observation, dict):
            raise TypeError("observation must be a dict")
        # Only narrow, allowlisted primitives leave the observer. Never echo raw
        # records or citizen data into the decision or audit output.
        if self.profile == "vtnd":
            march = observation.get("march_available")
            verified = observation.get("verified") is True
            safe = {"verified": verified, "march_available": march if type(march) is int else None}
            if type(march) is not int or march < 0:
                safe["march_available"] = None
        else:
            required = observation.get("required_fields")
            record = observation.get("record")
            if not isinstance(required, list) or not all(type(x) is str and 0 < len(x) <= 128 for x in required) or not isinstance(record, dict) or not required:
                return AgentResult(self.profile, "UNRESOLVED", "Invalid or incomplete input schema", 0.0, ("INVALID_SCHEMA",), {}, False)
            # Evaluate only presence, never persist or emit field values.
            missing = sum(record.get(field) is None or (isinstance(record.get(field), str) and not record[field].strip()) for field in required)
            return AgentResult(self.profile, "REVIEW" if missing else "PASS",
                "Review missing required fields" if missing else "No missing required fields detected",
                1.0, ("MISSING_FIELDS",) if missing else ("FIELDS_PRESENT",),
                {"missing_count": missing, "required_count": len(required)}, False)

        decision = self.reasoner.evaluate(safe)
        if decision.status not in ALLOWED_STATUSES or not math.isfinite(decision.confidence) or not 0 <= decision.confidence <= 1:
            return AgentResult(self.profile, "UNRESOLVED", "Safety gate rejected decision", 0.0, ("SAFETY_GATE",), {}, False)
        if not verified or safe["march_available"] is None:
            return AgentResult(self.profile, "UNRESOLVED", "Verify observation before review", 0.0, ("UNVERIFIED",), {}, False)
        memory_used = False
        details = {"march_available": safe["march_available"]}
        if memory_state is not None and isinstance(memory_state, dict):
            bias = memory_state.get("bias_seconds")
            samples = memory_state.get("samples")
            if (memory_state.get("namespace") == "vtnd" and type(samples) is int and samples > 0
                    and type(bias) in (float, int) and math.isfinite(bias) and abs(bias) <= 3600):
                memory_used = True
                details["eta_bias_seconds"] = float(bias)
                details["memory_samples"] = samples
        return AgentResult(self.profile, decision.status, decision.suggestion,
            decision.confidence, ("MARCH_EMPTY",) if decision.status == "WAITING" else ("MARCH_AVAILABLE_REVIEW",),
            details, memory_used)
