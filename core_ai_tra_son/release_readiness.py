"""v1.0.0 offline SHADOW release readiness; no automatic promotion or actions."""
from dataclasses import dataclass
from .quality_gate import QualityGate
from .recovery_audit import RecoveryAudit
from .decision_learning import DecisionLearner
from .recovery_governance import RecoveryGovernance


@dataclass(frozen=True)
class ReleaseReadiness:
    status: str
    reasons: tuple[str, ...]
    action_executed: bool = False
    production_approved: bool = False


def evaluate_readiness(*, quality, audit, entries, recovered_state,
                       provenance_verified=False, integrity_verified=False,
                       human_reviewed=False, shadow_only=True):
    """Independent inputs must be verified by caller; never authorizes production.

    The quality report is checked upstream; this gate accepts a QualityGate
    only. Audit authenticity is verified with the caller-owned RecoveryAudit.
    """
    if type(quality) is not QualityGate or type(audit) is not RecoveryAudit:
        raise ValueError("invalid evidence objects")
    phase = audit.verify(entries)
    reasons = []
    if quality.status != "PASS" or quality.action_executed or quality.discordant < 8:
        reasons.append("quality_gate_not_passed")
    if provenance_verified is not True:
        reasons.append("provenance_not_verified")
    if integrity_verified is not True:
        reasons.append("integrity_not_verified")
    if human_reviewed is not True:
        reasons.append("independent_review_missing")
    if shadow_only is not True:
        reasons.append("shadow_boundary_required")
    if not DecisionLearner.valid(recovered_state):
        reasons.append("invalid_learning_state")
    if phase not in ("PROPOSED", "CLOSED"):
        reasons.append("unresolved_recovery_lifecycle")
    if not RecoveryGovernance.learning_allowed(phase):
        # A recovery policy never unfreezes learning automatically.
        pass
    return ReleaseReadiness("PASS" if not reasons else "BLOCKED", tuple(reasons))
