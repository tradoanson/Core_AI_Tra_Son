"""Deterministic multi-signal SHADOW reasoning; no action execution or IO."""
from dataclasses import dataclass, asdict
import math

SIGNALS = frozenset({"march_available", "march_capacity", "eta_seconds", "return_buffer_seconds", "resource_available"})
MAX_SIGNALS = 5
MAX_ETA = 604800
MAX_BUFFER = 3600

@dataclass(frozen=True)
class ReasoningResult:
    status: str
    confidence: float
    reason_codes: tuple[str, ...]
    explanation: str
    evidence: dict
    action_executed: bool = False

    def to_dict(self):
        result = asdict(self)
        result["reason_codes"] = list(self.reason_codes)
        return result


class ReasoningEngine:
    """Evaluate verified, bounded VTND signals. Never dispatches actions."""
    def evaluate(self, signals: dict, *, verified: bool = False, memory_state: dict | None = None) -> ReasoningResult:
        def unresolved(code, explanation):
            return ReasoningResult("UNRESOLVED", 0.0, (code,), explanation, {})
        if not isinstance(signals, dict) or len(signals) > MAX_SIGNALS or not set(signals).issubset(SIGNALS):
            return unresolved("INVALID_SIGNALS", "Signal schema rejected")
        if verified is not True:
            return unresolved("UNVERIFIED", "Verified observations required")
        march = signals.get("march_available")
        if type(march) is not int or not 0 <= march <= 100:
            return unresolved("INVALID_MARCH", "March count is missing or invalid")
        capacity = signals.get("march_capacity")
        if capacity is not None:
            if type(capacity) is not int or not 0 <= capacity <= 100:
                return unresolved("INVALID_CAPACITY", "March capacity is invalid")
            if march > capacity:
                return unresolved("SIGNAL_CONFLICT", "Available march exceeds declared capacity")
        eta = signals.get("eta_seconds")
        buffer = signals.get("return_buffer_seconds")
        resource = signals.get("resource_available")
        if eta is not None and (type(eta) not in (int, float) or not math.isfinite(eta) or not 0 <= eta <= MAX_ETA):
            return unresolved("INVALID_ETA", "ETA must be finite and bounded")
        if buffer is not None and (type(buffer) not in (int, float) or not math.isfinite(buffer) or not 0 <= buffer <= MAX_BUFFER):
            return unresolved("INVALID_BUFFER", "Return buffer is invalid")
        if resource is not None and type(resource) is not bool:
            return unresolved("INVALID_RESOURCE", "Resource availability must be boolean")
        evidence = {"march_available": march}
        if capacity is not None:
            evidence["march_capacity"] = capacity
        codes = []
        score = 0.6
        if march == 0:
            codes.append("MARCH_EMPTY")
            status = "WAITING"
        else:
            codes.append("MARCH_AVAILABLE_REVIEW")
            status = "REVIEW"
        if eta is not None:
            evidence["eta_seconds"] = float(eta)
            codes.append("ETA_VERIFIED")
            score += 0.1
        if buffer is not None:
            evidence["return_buffer_seconds"] = float(buffer)
            codes.append("BUFFER_VERIFIED")
            score += 0.1
        if resource is not None:
            evidence["resource_available"] = resource
            codes.append("RESOURCE_VERIFIED")
            score += 0.1
            if march > 0 and resource is False:
                status = "WAITING"
                codes.append("RESOURCE_UNAVAILABLE")
        memory_used = False
        if isinstance(memory_state, dict):
            bias = memory_state.get("bias_seconds")
            samples = memory_state.get("samples")
            if (memory_state.get("namespace") == "vtnd" and type(samples) is int and 0 < samples <= 1_000_000_000
                    and type(bias) in (int, float) and math.isfinite(bias) and abs(bias) <= 3600):
                memory_used = True
                codes.append("MEMORY_CONTEXT")
                evidence["eta_bias_seconds"] = float(bias)
                if eta is not None:
                    evidence["adjusted_eta_seconds"] = max(0.0, float(eta) + float(bias))
                # Context is not independent verification; do not increase confidence.
        evidence["memory_used"] = memory_used
        confidence = round(min(0.9, score), 3)
        explanation = ("No march available; keep waiting" if march == 0 else
                       "Resource unavailable; keep waiting" if status == "WAITING" else
                       "March available; human review required")
        return ReasoningResult(status, confidence, tuple(codes), explanation, evidence)
