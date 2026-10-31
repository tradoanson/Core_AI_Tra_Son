# v0.6.3 — Learning Recovery & Concurrency Hardening

Status: CI PASS on branch (Python 3.11, 3.12, 3.13); merge pending.\n\nCI evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41200282252\nVersioned verification: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41200282310

Scope: POSIX flock sidecar for cross-process serialized checkpoint publication, SQLite transactional dedup, post-commit crash suffix reconciliation before next write, directory fsync for checkpoint rename, symlink lock rejection, bounded synthetic performance smoke.

Gates: >=215 tests on Python 3.11/3.12/3.13, versioned smoke, static safety, 8 independent subprocess writers, same-ID contention, crash exit after ledger commit, malformed checkpoint and suffix, 200-event growth regression, SHADOW no execution.

Limits: POSIX local filesystem only. Windows is deliberately unsupported (fail closed); no real power-cut testing, no multi-host/network-filesystem locking guarantee, no quantitative scaling benchmark or production testing. Caller attests verification. Key and checkpoint must be protected independently. No production integration.
