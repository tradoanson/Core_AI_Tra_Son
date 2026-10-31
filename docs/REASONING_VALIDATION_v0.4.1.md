# Reasoning Validation & Calibration diagnostics v0.4.1

```python
from core_ai_tra_son.validation import BenchmarkCase, validate_benchmark
cases = [
    BenchmarkCase("empty", {"march_available": 0}, True, "WAITING"),
    BenchmarkCase("conflict", {"march_available": 5, "march_capacity": 4}, True, "UNRESOLVED"),
]
report = validate_benchmark(cases)
print(report.to_dict())
```

- Explicit capacity conflict: available marches exceeding declared capacity -> UNRESOLVED with SIGNAL_CONFLICT, no evidence echo.
- Repeatability: repeated and parallel evaluations must yield identical structured outputs.
- Diagnostic bins: compare deterministic confidence heuristic against expected-status agreement for synthetic fixtures. This is **not** statistical probability calibration.
- Guardrails: max 512 benchmark cases; bounded IDs; no disk writes, network or execution. Case identifiers should be synthetic and must not contain personal information.
- Future actual calibration requires independently labelled, representative, privacy-reviewed observations, calibration curves and external validation. No such data are used here.
