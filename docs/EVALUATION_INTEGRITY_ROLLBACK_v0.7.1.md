# Evaluation Integrity & Persistent Rollback v0.7.1

```python
from core_ai_tra_son.evaluation_integrity import EvaluationIntegrityStore
from core_ai_tra_son.decision_learning import DecisionLearningState
store = EvaluationIntegrityStore("isolated.sqlite3", "anchor.json", secret_key,
                                 "signed_evaluation.json", "rollback_override.json")
store.initialize()
store.bootstrap()
# after explicit verified learning and independent synthetic holdout:
report = store.evaluate_holdout(holdout_cases)
signed = store.verify_evaluation()
if report.status == "DEGRADED":
    store.activate_rollback(DecisionLearningState())
effective = store.effective_state()
```

Evaluation rejects exact event ID overlap with learning ledger and duplicate holdout IDs. It signs a bounded summary and holdout SHA-256 with the caller-provided HMAC key, bound to ledger count/head. It never persists raw holdout signals. Signed report and override use create-only atomic publication.

On DEGRADED evidence, an explicitly supplied valid older learning state can be persisted as an authenticated *selection override*. Ledger and checkpoint are never rewritten; further writes through this class fail closed while override is present. Missing, tampered, stale or conflicting artifacts fail closed.

Security limitations: semantically identical events with different IDs cannot be identified; provenance is caller-attested. A caller holding the HMAC key can forge reports. The previous state is caller-supplied and validated structurally, not independently reconstructed from an earlier checkpoint. No auto-clear or auto-rewrite; manual recovery requires a separate reviewed process. Linux POSIX local filesystem only. SHADOW and GitHub Actions only.
