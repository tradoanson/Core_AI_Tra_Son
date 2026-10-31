# Advanced Reasoning v0.5.0

```python
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner
r = AdvancedReasoner().rank(
    {"march_available": 2, "eta_seconds": 20,
     "return_buffer_seconds": 300, "resource_available": True},
    verified=True, options=["WAIT", "REVIEW_GATHER", "REVIEW_RETURN"])
print(r.to_dict())
```

The engine compares up to eight unique allowlisted options (currently three distinct options), assigns deterministic policy scores, sorts descending by score and then alphabetically by option ID, and explains each option. It refuses ranking when base signal verification fails. REVIEW_GATHER and REVIEW_RETURN are human review suggestions, not dispatch instructions.

Fixed policy score is not a probability or validated measure of utility. Return timing uses verified ETA and buffer, optionally adjusted by supplied memory context. No network, host actions, persistence or real citizen data.
