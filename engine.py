from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class Decision:
    status: str
    suggestion: str
    confidence: float
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class CoreAI:
    """Read-only agent; never writes to the host application's data."""
    def __init__(self, profile: str):
        if profile not in {"vtnd", "nhankhau"}:
            raise ValueError("Unsupported profile")
        self.profile = profile

    def evaluate(self, observation: dict[str, Any]) -> Decision:
        if not isinstance(observation, dict):
            raise TypeError("observation must be a dict")
        if self.profile == "vtnd":
            march = observation.get("march_available")
            verified = observation.get("verified") is True
            if not verified or not isinstance(march, int) or isinstance(march, bool) or march < 0:
                return Decision("UNRESOLVED", "Do not dispatch; verify state", 0.0, {})
            if march == 0:
                return Decision("WAITING", "Keep current scheduler", 1.0, {"march_available": march})
            return Decision("REVIEW", "March available; use existing verified workflow", 1.0, {"march_available": march})
        errors = []
        required = observation.get("required_fields", [])
        record = observation.get("record", {})
        if not isinstance(required, list) or not all(isinstance(x, str) for x in required) or not isinstance(record, dict):
            return Decision("UNRESOLVED", "Invalid input schema", 0.0, {})
        for field in required:
            if record.get(field) is None or (isinstance(record.get(field), str) and not record[field].strip()):
                errors.append(field)
        return Decision("REVIEW" if errors else "PASS", "Review missing required fields" if errors else "No missing required fields detected", 1.0, {"missing_fields": errors})
