"""Pure, bounded, read-only diagnostics for v3.2 integration requests.

Never interprets caller-asserted verification as independent proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .integration_contract import IntegrationRequest, validate_request

MAX_REASON_LENGTH = 80


@dataclass(frozen=True)
class ContractDiagnostic:
    accepted: bool
    reason: str
    mode: str
    independently_verified: bool = False


def diagnose_contract(request: Any) -> ContractDiagnostic:
    """Fail closed for wrong input types, without reading host resources."""
    if not isinstance(request, IntegrationRequest):
        return ContractDiagnostic(False, "invalid_request_type", "shadow")
    try:
        result = validate_request(request)
    except (TypeError, ValueError, AttributeError):
        return ContractDiagnostic(False, "invalid_request_shape", "shadow")
    reason = result.reason
    if not isinstance(reason, str) or len(reason) > MAX_REASON_LENGTH:
        return ContractDiagnostic(False, "invalid_reason", "shadow")
    return ContractDiagnostic(result.accepted, reason, "shadow")
