"""Pure, bounded, read-only diagnostics for v3.2 integration requests.

Never interprets caller-asserted verification as independent proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .integration_contract import IntegrationRequest, validate_request

MAX_REASON_LENGTH = 80
MAX_OBSERVATION_FIELDS = 64
MAX_FIELD_NAME_LENGTH = 128
MAX_TEXT_VALUE_LENGTH = 4096


@dataclass(frozen=True)
class ContractDiagnostic:
    accepted: bool
    reason: str
    mode: str
    independently_verified: bool = False


def diagnose_contract(request: Any) -> ContractDiagnostic:
    """Fail closed for wrong input types, without reading host resources."""
    if type(request) is not IntegrationRequest:
        return ContractDiagnostic(False, "invalid_request_type", "shadow")
    if type(request.verified) is not bool:
        return ContractDiagnostic(False, "invalid_verified_type", "shadow")
    if type(request.project) is not str or type(request.contract_version) is not str:
        return ContractDiagnostic(False, "invalid_metadata_type", "shadow")
    if type(request.observation) is not dict:
        return ContractDiagnostic(False, "invalid_observation_type", "shadow")
    if len(request.observation) > MAX_OBSERVATION_FIELDS:
        return ContractDiagnostic(False, "observation_too_large", "shadow")
    if any(type(k) is not str or not k or len(k) > MAX_FIELD_NAME_LENGTH for k in request.observation):
        return ContractDiagnostic(False, "invalid_observation_keys", "shadow")
    if any(type(v) is str and len(v) > MAX_TEXT_VALUE_LENGTH for v in request.observation.values()):
        return ContractDiagnostic(False, "observation_text_too_large", "shadow")
    try:
        result = validate_request(request)
    except (TypeError, ValueError, AttributeError):
        return ContractDiagnostic(False, "invalid_request_shape", "shadow")
    reason = result.reason
    if not isinstance(reason, str) or len(reason) > MAX_REASON_LENGTH:
        return ContractDiagnostic(False, "invalid_reason", "shadow")
    return ContractDiagnostic(result.accepted, reason, "shadow")
