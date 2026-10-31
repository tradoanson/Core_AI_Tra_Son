# v0.6.2 — Learning Security & Performance

Status: PENDING final GitHub Actions and merge.

Scope: opt-in independent HMAC-SHA256 checkpoint, caller-managed >=32-byte secret, anchored history rollback detection, incremental verified suffix replay, explicit reconciliation of valid post-crash suffix.

Acceptance: >=190 tests, clean install, Python 3.11–3.13, checkpoint tamper/wrong key/rollback, concurrent same-instance updates, crash recovery, safety and backwards compatibility.

Limitations: The checkpoint must be stored independently from the SQLite ledger and the secret key separately secured. Without those operational controls, an attacker can replace both ledger and checkpoint. Incremental validation checks the anchored head and suffix, not every old row; first bootstrap fully replays. This version serializes concurrent threads on a single store instance, but does not guarantee correct checkpoint publication across multiple processes or independent instances sharing one checkpoint. No crash-injection/OS power-loss tests, performance benchmarks or production tests; only synthetic GitHub Actions. No automatic actions.
