"""Conservative paired SHADOW quality gate; synthetic holdouts only."""
from dataclasses import dataclass
from math import comb
from .decision_quality import QualityReport

@dataclass(frozen=True)
class QualityGate:
    status: str
    improvements: int
    regressions: int
    discordant: int
    exact_p_value: float
    action_executed: bool = False

def paired_quality_gate(report, *, minimum_discordant=8, alpha=0.05):
    """Exact one-sided paired sign test on changed decisions.

    A PASS is statistical evidence on the caller-supplied holdout, not proof
    of live benefit. Abstentions and dependent cases may invalidate inference.
    """
    if type(report) is not QualityReport or report.action_executed:
        raise ValueError("invalid report")
    if type(minimum_discordant) is not int or not 1 <= minimum_discordant <= 512:
        raise ValueError("invalid sample gate")
    if type(alpha) not in (float,int) or not 0 < alpha <= 0.5:
        raise ValueError("invalid alpha")
    wins, losses = len(report.improvements), len(report.regressions)
    n = wins + losses
    if n > report.evaluated or report.evaluated > report.total or report.evaluated < 0:
        raise ValueError("inconsistent report counts")
    if report.status == "INSUFFICIENT_EVIDENCE" or n < minimum_discordant:
        return QualityGate("INSUFFICIENT_EVIDENCE", wins, losses, n, 1.0)
    p = sum(comb(n,k) for k in range(wins,n+1)) / (2**n)
    status = "PASS" if wins > losses and p <= alpha and report.status == "PASS" else "DEGRADED"
    return QualityGate(status,wins,losses,n,round(p,10))
