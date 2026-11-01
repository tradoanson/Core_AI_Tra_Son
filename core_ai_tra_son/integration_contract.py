"""Versioned read-only integration contract for Core AI v3.2.0.

No host imports, network, filesystem writes or execution side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

CONTRACT_VERSION = "3.2.0"
SUPPORTED_PROJECTS = frozenset({"vtnd", "nhankhau"})


@dataclass(frozen=True)
class IntegrationRequest:
    project: str
    observation: Mapping[str, Any]
    verified: bool = False
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class IntegrationResult:
    accepted: bool
    reason: str
    project: str
    contract_version: str = CONTRACT_VERSION
    mode: str = "shadow"


def validate_request(request: IntegrationRequest) -> IntegrationResult:
    """Fail closed; validation never executes an action or calls a host."""
    if request.contract_version != CONTRACT_VERSION:
        return IntegrationResult(False, "unsupported_contract_version", request.project)
    if request.project not in SUPPORTED_PROJECTS:
        return IntegrationResult(False, "unsupported_project", request.project)
    if not isinstance(request.observation, Mapping):
        return IntegrationResult(False, "invalid_observation", request.project)
    if not request.verified:
        return IntegrationResult(False, "unverified_observation", request.project)
    if not request.observation:
        return IntegrationResult(False, "empty_observation", request.project)
    return IntegrationResult(True, "validated_read_only", request.project)
