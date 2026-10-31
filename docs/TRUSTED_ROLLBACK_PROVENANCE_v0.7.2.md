# Trusted Rollback & Evaluation Provenance v0.7.2

The optional TrustedEvaluationStore requires three **independent caller-owned keys**: ledger, holdout issuer, and rollback approver. The issuer signs a canonical digest of holdout cases and their IDs; the store verifies the signature and exact training/holdout ID separation before evaluation. The approver signs a ledger-bound rollback request. The store replays historical ledger events to derive the earlier state and persists a create-only HMAC-authenticated selection override; it never rewrites the ledger.

An issuer signature proves possession of the configured issuer key, **not** that a real independent reviewer checked the data. Independent validation, secure key custody, and source attestation are operational responsibilities. Semantic duplicates under different IDs remain undetected. The signed evaluation report contains a digest rather than raw signals. Approval must be a separate caller-controlled step. Rollback remains frozen, SHADOW only.

Current constraints: Linux POSIX local filesystem; no Windows or production integration. No automatic learning reactivation. The prefix replay is O(N) by design and should not run continuously.
