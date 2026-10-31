# Adaptive Memory v0.2.0 — developer usage

```python
from core_ai_tra_son.memory import AdaptiveMemory

memory = AdaptiveMemory("my_dedicated_adaptive.sqlite3", namespace="vtnd", alpha=0.2)
memory.initialize()  # explicit permission to create a dedicated local DB
memory.observe(300, 315, verified=True)
print(memory.correct(300))
print(memory.state())
```

- No ML training; exponential moving average correction only.
- A sample is ignored when `verified` is not literally `True`.
- Rejects non-finite, negative, out-of-range values and error magnitude >3600 s.
- Separate namespaces share a file but not their bias or sample counts.
- Restart persistence: instantiate a new object with the same path and namespace.
- **Do not point at host application's database.** No automatic host integration.
- Source of truth is `core_ai_tra_son/`, not legacy root modules.
