"""Bounded in-memory, sanitized SHADOW audit trail. No disk or network writes."""
from collections import deque
from dataclasses import dataclass
from .agent import AgentResult

ALLOWED_REASONS = frozenset({
    "INVALID_SCHEMA", "RESOURCE_LIMIT", "MISSING_FIELDS", "FIELDS_PRESENT",
    "SAFETY_GATE", "UNVERIFIED", "MARCH_EMPTY", "MARCH_AVAILABLE_REVIEW",
})
ALLOWED_STATUSES = frozenset({"UNRESOLVED", "WAITING", "REVIEW", "PASS"})
ALLOWED_PROFILES = frozenset({"vtnd", "nhankhau"})

@dataclass(frozen=True)
class AuditEntry:
    sequence: int
    profile: str
    status: str
    reason_codes: tuple[str, ...]
    memory_used: bool
    action_executed: bool

    def to_dict(self):
        return {"sequence": self.sequence, "profile": self.profile, "status": self.status,
                "reason_codes": list(self.reason_codes), "memory_used": self.memory_used,
                "action_executed": self.action_executed}


class SafeAuditLog:
    """Caller-owned bounded ring; stores no raw observation, IDs or free-text."""
    def __init__(self, capacity: int = 256):
        if type(capacity) is not int or not 1 <= capacity <= 4096:
            raise ValueError("capacity must be an integer in [1, 4096]")
        self._entries = deque(maxlen=capacity)
        self._sequence = 0

    def record(self, result: AgentResult) -> AuditEntry:
        if not isinstance(result, AgentResult):
            raise TypeError("result must be AgentResult")
        if result.profile not in ALLOWED_PROFILES or result.status not in ALLOWED_STATUSES:
            raise ValueError("unrecognized agent result")
        if type(result.action_executed) is not bool or result.action_executed:
            raise ValueError("audit only accepts non-executing SHADOW results")
        if type(result.memory_used) is not bool:
            raise ValueError("invalid memory flag")
        if not isinstance(result.reason_codes, tuple) or not all(
                type(code) is str and code in ALLOWED_REASONS for code in result.reason_codes):
            raise ValueError("unrecognized reason code")
        self._sequence += 1
        entry = AuditEntry(self._sequence, result.profile, result.status,
                           result.reason_codes, result.memory_used, False)
        self._entries.append(entry)
        return entry

    def snapshot(self):
        return [entry.to_dict() for entry in self._entries]

    def __len__(self):
        return len(self._entries)
