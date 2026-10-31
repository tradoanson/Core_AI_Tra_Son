# Reasoning Engine v0.4.0

```python
from core_ai_tra_son.reasoning import ReasoningEngine
r = ReasoningEngine().evaluate(
    {"march_available": 1, "eta_seconds": 300,
     "return_buffer_seconds": 300, "resource_available": True},
    verified=True,
    memory_state={"namespace": "vtnd", "samples": 4, "bias_seconds": 15})
print(r.to_dict())
```

The engine produces WAITING, REVIEW or UNRESOLVED with reason codes, bounded confidence and allowlisted evidence. It cannot dispatch, modify a game, read citizen databases, call a network endpoint or write an audit file. Memory state must be supplied by a trusted caller; this engine does not independently validate SQLite provenance.

Confidence represents completeness of validated input signals, not prediction accuracy. This is a deterministic rules engine, not a trained language model.
