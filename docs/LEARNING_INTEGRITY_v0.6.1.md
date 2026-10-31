# Learning Integrity & Persistence v0.6.1

```python
from core_ai_tra_son.learning_store import LearningStore
store = LearningStore("/dedicated/shadow_learning.sqlite3")
store.initialize()  # explicit creation; refuses unrelated existing databases
store.observe("synthetic-event-001", "REVIEW_GATHER", successful=True, verified=True)
state = store.state()
store.backup("/dedicated/backup.sqlite3")  # destination must not exist
# Recovery must target a separate nonexistent database:
recovered = LearningStore("/dedicated/recovered.sqlite3")
recovered.restore("/dedicated/backup.sqlite3")
```

- SQLite transaction + unique event ID prevents duplicate verified outcome updates, including concurrent callers.
- Same ID with conflicting label or option is rejected. IDs are opaque synthetic identifiers, not personal data.
- Hash-linked event ledger is replayed and validated before state is used; invalid chain, SQLite corruption or unsupported schema fail closed.
- Online backup uses SQLite backup API, restore validates staged snapshot and atomically publishes to a nonexistent target. No overwrite.
- This storage is opt-in and dedicated; it is **not** connected to Auto VTND, Nhân Khẩu or host application databases.
- Hash chain is not tamper-proof against an adversary able to rewrite the database and hashes. Tail truncation cannot be detected without externally anchored state. Verification is caller-attested. Full replay per update is intentionally conservative but expensive for large histories.
