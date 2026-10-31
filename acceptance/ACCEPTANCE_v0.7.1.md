# v0.7.1 — Evaluation Integrity & Persistent Rollback

Status: CI PASS on branch (Python 3.11, 3.12, 3.13); merge pending.\n\nCI evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41200939960\nVersioned verification: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41200939964

Gates: >=265 tests, Python 3.11/3.12/3.13, exact training/holdout event-ID overlap detection, HMAC-SHA256 signed bounded report bound to authenticated ledger count/head, create-only artifact, rollback override persisted and authenticated, tamper/stale/missing fail closed, freeze further learning under override, no host actions.

Important limits: Only exact event-ID overlap is checked, not semantic duplication under different IDs. Verification and holdout independence are caller-attested. The rollback is a **non-destructive persisted selection override**, not deletion or rewind of SQLite ledger/checkpoint. It is intentionally frozen until an operator-managed migration/review; no automatic reactivation. No production testing, Linux POSIX only.
