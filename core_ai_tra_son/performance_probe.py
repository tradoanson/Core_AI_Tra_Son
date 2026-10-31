"""Bounded offline reasoning latency probe; no IO or host dispatch."""
from dataclasses import dataclass
from time import perf_counter
from .advanced_reasoning import AdvancedReasoner

@dataclass(frozen=True)
class PerformanceProbe:
    iterations: int
    elapsed_ms: float
    average_ms: float
    maximum_ms: float
    budget_passed: bool
    action_executed: bool = False

def benchmark_shadow(signals, *, iterations=100, budget_ms=100.0):
    if type(signals) is not dict or type(iterations) is not int or not 1 <= iterations <= 1000:
        raise ValueError("bounded benchmark inputs required")
    if type(budget_ms) not in (int,float) or not 0 < budget_ms <= 60000:
        raise ValueError("invalid latency budget")
    engine=AdvancedReasoner()
    worst=0.0
    start=perf_counter()
    for _ in range(iterations):
        t=perf_counter()
        result=engine.rank(signals,verified=True,options=["WAIT","REVIEW_GATHER","REVIEW_RETURN"])
        if result.action_executed:
            raise ValueError("host action detected")
        worst=max(worst,(perf_counter()-t)*1000)
    elapsed=(perf_counter()-start)*1000
    return PerformanceProbe(iterations,elapsed,elapsed/iterations,worst,worst <= budget_ms)
