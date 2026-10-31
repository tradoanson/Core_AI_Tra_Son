"""Read-only recovery governance decisions for the SHADOW rollback lifecycle.

No filesystem writes, key management, host dispatch or implicit unfreeze.
"""
from dataclasses import dataclass
from .decision_learning import DecisionLearner


@dataclass(frozen=True)
class RecoveryDecision:
    phase: str
    eligible: bool
    reason: str
    requires_manual_approval: bool = True
    action_executed: bool = False


class RecoveryGovernance:
    """Deterministic gate: PROPOSED -> REVIEWED -> APPROVED -> ACTIVE -> CLOSED.

    CLOSED does not delete the override or resume learning. Separate explicit
    audited storage migration is required; no automated transition to writable.
    """
    PHASES = ("PROPOSED", "REVIEWED", "APPROVED", "ACTIVE", "CLOSED")

    @classmethod
    def transition(cls, phase, target, *, evidence_valid=False,
                   independent_reviewer=False, independent_approver=False,
                   override_valid=False, closure_reviewed=False):
        if phase not in cls.PHASES or target not in cls.PHASES:
            raise ValueError("invalid lifecycle phase")
        next_phase = {"PROPOSED":"REVIEWED", "REVIEWED":"APPROVED",
                      "APPROVED":"ACTIVE", "ACTIVE":"CLOSED"}.get(phase)
        if target != next_phase:
            return RecoveryDecision(phase, False, "invalid transition")
        gates = {
            "REVIEWED": evidence_valid is True and independent_reviewer is True,
            "APPROVED": evidence_valid is True and independent_approver is True,
            "ACTIVE": evidence_valid is True and override_valid is True,
            "CLOSED": closure_reviewed is True and independent_approver is True,
        }
        if not gates[target]:
            return RecoveryDecision(phase, False, "missing independent evidence or approval")
        return RecoveryDecision(target, True, "manual governance gate passed")

    @staticmethod
    def learning_allowed(phase, *, override_present=False):
        if phase not in RecoveryGovernance.PHASES:
            raise ValueError("invalid lifecycle phase")
        # Never infer safe automatic reactivation from a governance label.
        return False

    @staticmethod
    def validate_recovered_state(state):
        return DecisionLearner.valid(state)
