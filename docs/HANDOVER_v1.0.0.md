# Core AI Trà Sơn v1.0.0 — Handover

## What is delivered
Python package `core-ai-tra-son` with deterministic read-only SHADOW recommendation, bounded verified-only adaptation, SQLite event ledger, authenticated checkpoints, POSIX flock concurrency, synthetic holdout evaluation, HMAC-signed evaluation summaries, independent issuer/approver key hooks, historical replay rollback override, recovery governance and audit, paired quality gate and offline readiness assessment.

## Where to inspect
- `pyproject.toml`: package version.
- `core_ai_tra_son/`: source modules.
- `tests/`: automated safety and functionality tests.
- `scripts/release_smoke.py`: isolated package smoke test.
- `.github/workflows/release-acceptance-v1.0.0.yml`: Python 3.11–3.13 acceptance.
- `acceptance/ACCEPTANCE_v1.0.0.md`: acceptance record.

## Safe operational posture
No automatic action, no production deployment, no integration with Auto VTND or Web Nhân Khẩu, no real citizen data. Signing keys must be supplied and managed outside GitHub source. The program does not independently authenticate real-world reviewers or data. Learning rollback is a signed, non-destructive *selection override* and freezes further learning; it does not rewrite original history. Windows native locking, semantic leakage prevention, external provenance attestation, independently durable audit anchor, realistic quality evaluation and production hardening remain future work.

## Release status
Release v1.0.0 is a **SHADOW prototype milestone**, not production readiness certification. Do not use it to control any host or handle sensitive live records.
