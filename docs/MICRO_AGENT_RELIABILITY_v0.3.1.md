# Micro Agent Reliability v0.3.1

```python
from core_ai_tra_son.agent import MicroAgent
from core_ai_tra_son.audit import SafeAuditLog

agent = MicroAgent("vtnd")
audit = SafeAuditLog(capacity=256)
decision = agent.evaluate({"verified": True, "march_available": 1})
audit.record(decision)
print(audit.snapshot())
```

Input caps: 64 observation keys, 128 distinct required fields, 256 record keys, 128-character field names, maximum 1 billion accepted memory samples. Exceeding limits yields UNRESOLVED or ignores invalid memory.

Audit log is volatile and sanitized. It does not write files, contain raw personal data, execute host actions or provide permanent evidence. Use a separately reviewed persistence design if durable logs become necessary.
