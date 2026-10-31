# v0.6.1 — Learning Integrity & Persistence

Status: PENDING final GitHub Actions and merge.

Scope: explicit dedicated SQLite learning event ledger, atomic BEGIN IMMEDIATE, unique opaque event IDs, verified-only feedback, hash-linked event replay and bounded learning, online SQLite backup and fail-closed restore to a nonexistent path.

Acceptance: >=160 tests, clean install, offline smoke, Python 3.11/3.12/3.13, dedup under concurrent threads, conflict rejection, tamper detection, corruption rejection, backup/restore non-overwrite and SHADOW safety.

Limitations: Hash chain is unkeyed and can be recomputed by a malicious writer; deletion of trailing events is not detectable without external anchored checkpoint. Caller supplies verified=True; source authenticity is not independently verified. Each update replays the entire bounded event ledger, so performance degrades with history size; no production integration or real-machine testing.
