# Micro Agent Engine v0.3.0

```python
from core_ai_tra_son.agent import MicroAgent

agent = MicroAgent("vtnd")
result = agent.evaluate({"verified": True, "march_available": 1},
    memory_state={"namespace": "vtnd", "bias_seconds": 12.5, "samples": 3})
print(result.to_dict())
```

Pipeline: allowlisted Observer -> optional memory context -> CoreAI Reasoner -> Safety Gate -> structured Decision Logger output.

The output is **advisory only**. It never dispatches a march, changes citizen records, calls a host API, or writes an audit file. For nhankhau, only counts of missing fields are returned; raw personal record values are excluded.

No background services, network calls or automatic host integration. This version is rules-based, not a trained AI model.
