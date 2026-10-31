# Core AI Trà Sơn v1.0.0 — Offline SHADOW Release Acceptance

Status: PENDING CI and merge.

Criteria: >=343 tests, Python 3.11/3.12/3.13, isolated editable installation, smoke test outside repository, no external dependencies, static safety, conservative fail-closed release gate.

Scope: read-only offline advisory prototype, opt-in isolated learning and evaluation, authenticated checkpoints and non-destructive rollback, independent provenance and approval hooks, audit protocol, quality gates. **No host actions, production deployment or integration.**

Known limitations: issuer and reviewer identity caller-attested; no independently anchored anti-truncation audit storage; semantic duplicates can evade ID overlap check; holdout quality is synthetic; statistical assumptions not verified; no Windows cross-process lock support; rollback override freezes learning and requires manual process to clear. No real-world quality or security certification.
