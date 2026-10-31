"""Deterministic, bounded SHADOW ranking of predefined advisory alternatives.

No host actions, disk/network IO, model inference or private-record output.
"""
from dataclasses import dataclass, asdict
import math
from .reasoning import ReasoningEngine

MAX_OPTIONS = 8
ALLOWED_OPTIONS = frozenset({"WAIT", "REVIEW_GATHER", "REVIEW_RETURN"})
RISK_PENALTY = {"WAIT": 0.0, "REVIEW_GATHER": 0.1, "REVIEW_RETURN": 0.05}


@dataclass(frozen=True)
class RankedOption:
    option: str
    rank: int
    score: float
    reason_codes: tuple[str, ...]
    explanation: str

    def to_dict(self):
        data = asdict(self)
        data["reason_codes"] = list(self.reason_codes)
        return data


@dataclass(frozen=True)
class RankingResult:
    status: str
    confidence: float
    selected: str | None
    alternatives: tuple[RankedOption, ...]
    explanation: str
    reason_codes: tuple[str, ...]
    action_executed: bool = False

    def to_dict(self):
        data = asdict(self)
        data["alternatives"] = [x.to_dict() for x in self.alternatives]
        data["reason_codes"] = list(self.reason_codes)
        return data


class AdvancedReasoner:
    """Rank human-review options only when base reasoning verifies signals."""
    def __init__(self):
        self._base = ReasoningEngine()

    def rank(self, signals: dict, *, verified: bool = False, options=None,
             memory_state: dict | None = None) -> RankingResult:
        def reject(code, explanation):
            return RankingResult("UNRESOLVED", 0.0, None, (), explanation, (code,))
        if type(options) not in (list, tuple) or not 1 <= len(options) <= MAX_OPTIONS:
            return reject("INVALID_OPTIONS", "A bounded option list is required")
        if (any(type(x) is not str or x not in ALLOWED_OPTIONS for x in options)
                or len(set(options)) != len(options)):
            return reject("INVALID_OPTIONS", "Unknown or duplicate option")
        base = self._base.evaluate(signals, verified=verified, memory_state=memory_state)
        if base.status == "UNRESOLVED":
            return reject("BASE_UNRESOLVED", "Signal validation failed; ranking withheld")
        march = base.evidence["march_available"]
        resource = base.evidence.get("resource_available")
        eta = base.evidence.get("adjusted_eta_seconds", base.evidence.get("eta_seconds"))
        buffer = base.evidence.get("return_buffer_seconds")
        scores = {}
        reasons = {}
        explanations = {}
        # Scores are deterministic decision-policy priorities, not learned utilities.
        for option in options:
            if option == "WAIT":
                scores[option] = 0.7 if march == 0 or resource is False else 0.3
                reasons[option] = ("SAFE_WAIT",)
                explanations[option] = "No intervention; waiting is preferred when marches or resources are unavailable"
            elif option == "REVIEW_GATHER":
                if march == 0 or resource is not True:
                    scores[option] = 0.0
                    reasons[option] = ("GATHER_BLOCKED",)
                    explanations[option] = "Gather review blocked: verified available march and resource=True are both required"
                else:
                    scores[option] = 0.75 - RISK_PENALTY[option]
                    reasons[option] = ("MARCH_AVAILABLE", "RESOURCE_VERIFIED")
                    explanations[option] = "Verified march and resource availability permit human review of gathering"
            else:
                if march == 0 or resource is False or eta is None or buffer is None:
                    scores[option] = 0.0
                    reasons[option] = ("RETURN_CONTEXT_MISSING",)
                    explanations[option] = "Return review blocked: march, ETA, buffer and non-conflicting resource state required"
                else:
                    scores[option] = (0.8 if eta <= buffer else 0.4) - RISK_PENALTY[option]
                    reasons[option] = ("RETURN_DUE",) if eta <= buffer else ("RETURN_NOT_DUE",)
                    explanations[option] = ("Adjusted ETA is within the return buffer; human review is timely"
                                            if eta <= buffer else "ETA exceeds return buffer; return review has lower priority")
        ordered = sorted(options, key=lambda x: (-scores[x], x))
        if all(scores[x] == 0 for x in ordered):
            return reject("NO_SAFE_OPTION", "No eligible recommendation in supplied options")
        ranked = []
        for i, option in enumerate(ordered):
            codes = reasons[option]
            explanation = explanations[option]
            ranked.append(RankedOption(option, i + 1, round(scores[option], 3), codes, explanation))
        selected = ranked[0]
        if selected.score <= 0:
            return reject("NO_SAFE_OPTION", "No eligible recommendation")
        return RankingResult("REVIEW" if selected.option != "WAIT" else "WAITING",
                             base.confidence, selected.option, tuple(ranked),
                             ("Selected " + selected.option + " (score " + format(selected.score, ".3f") +
                              "); alternatives ranked by fixed policy score, then option ID. " +
                              selected.explanation),
                             ("RANKED_ADVISORY",))
