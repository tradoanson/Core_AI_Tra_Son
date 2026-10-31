"""Bounded offline resource sampling; no third-party dependencies or host actions."""
from dataclasses import dataclass
from time import perf_counter, process_time
import tracemalloc
from .advanced_reasoning import AdvancedReasoner

@dataclass(frozen=True)
class ResourceSample:
    iterations: int
    wall_ms: float
    cpu_ms: float
    peak_traced_bytes: int
    average_wall_ms: float
    action_executed: bool = False

def measure_shadow_resources(signals, *, iterations=25):
    if type(signals) is not dict or type(iterations) is not int or not 1 <= iterations <= 200:
        raise ValueError("bounded inputs required")
    if tracemalloc.is_tracing():
        raise ValueError("independent tracemalloc session required")
    engine=AdvancedReasoner()
    tracemalloc.start()
    try:
        wall=perf_counter()
        cpu=process_time()
        for _ in range(iterations):
            result=engine.rank(signals,verified=True,options=["WAIT","REVIEW_GATHER","REVIEW_RETURN"])
            if result.action_executed:
                raise ValueError("host action detected")
        wall_ms=(perf_counter()-wall)*1000
        cpu_ms=(process_time()-cpu)*1000
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return ResourceSample(iterations,round(wall_ms,3),round(cpu_ms,3),peak,round(wall_ms/iterations,3))
