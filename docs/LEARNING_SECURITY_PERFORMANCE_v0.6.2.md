# Learning Security & Performance v0.6.2

```python
from core_ai_tra_son.secure_learning import SecureLearningStore
key = b"<caller-provided-32-or-more-random-bytes>"  # example only; never commit keys
store = SecureLearningStore("/dedicated/learning.sqlite3",
                            "/separate/checkpoint.json", key)
store.initialize()
store.bootstrap()  # explicit one-time trust ceremony; full replay
store.observe("opaque-event-001", "REVIEW_GATHER", successful=True, verified=True)
state = store.state()
store.reconcile()  # only after an interrupted write/checkpoint update
```

An independent HMAC checkpoint anchors the event count, head hash and bounded learning state. Invalid checkpoint, wrong key, missing anchored history or rewritten head fail closed. Each subsequent write validates the anchor and replays only events after it; no full historical replay per update. Explicit reconcile handles a committed event with a stale checkpoint after an interrupted publication.

Security assumptions: caller protects secret key and stores checkpoint separately from database/backups. No independently authenticated outcome provenance; verified=True is still caller-attested. A malicious writer with both key and checkpoint access can forge history. Do not auto-bootstrap if checkpoint disappears.

Concurrency: one SecureLearningStore instance serializes thread updates; multiple independent instances/processes sharing a checkpoint are not supported for concurrent writes. Do not use with production apps. Performance gains are architectural, not benchmarked. SHADOW only.
