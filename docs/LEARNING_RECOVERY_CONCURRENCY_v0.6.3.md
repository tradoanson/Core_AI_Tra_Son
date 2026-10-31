# Learning Recovery & Concurrency Hardening v0.6.3

```python
from core_ai_tra_son.hardened_learning import HardenedLearningStore
store = HardenedLearningStore("/isolated/learning.sqlite3",
                              "/independent/checkpoint.json", secret_key_bytes)
store.initialize()
store.bootstrap()  # explicit first-time trust only
store.observe("opaque-event-1", "REVIEW_GATHER", successful=True, verified=True)
store.reconcile()  # explicit validated recovery if needed
```

An OS-level POSIX advisory flock on a persistent sidecar lock file serializes checkpoint publication among cooperating instances/processes. SQLite BEGIN IMMEDIATE preserves transactional dedup. After a crash between event commit and checkpoint publication, the next write validates the authenticated suffix, advances the checkpoint and then appends. Atomic same-directory replace and directory fsync harden checkpoint durability. Lock file is never removed in normal operation.

Trade-offs: the lock serializes writers, lowering peak throughput but preventing stale checkpoint overwrite. Only local POSIX filesystems with working flock and directory fsync are supported. Windows, network filesystems, malicious uncooperative writers, key compromise and true power-loss durability remain unverified. The 200-event synthetic smoke is a regression check, not a throughput benchmark. Core AI remains isolated SHADOW with no host actions.
