# v0.3.1 — Micro Agent Reliability

Status: PENDING final GitHub Actions and merge evidence.

Scope: bounded observation and required-fields inputs, bounded memory sample count, deterministic SHADOW results, parallel evaluation consistency, in-memory sanitized audit ring, fail-closed malformed inputs.

Acceptance: >=60 tests; Python 3.11/3.12/3.13; clean install; original regression and static safety gates; no host integration.

Audit ring stores only allowlisted profile, status, reason codes, memory-used and action-executed flags plus monotonic sequence. It deliberately stores no observations, free-text suggestions, citizen values, timestamps or disk records. Bounded capacity 1–4096 with FIFO eviction.

Limitations: In-memory audit is not durable, not cryptographically tamper-evident and not intended for evidentiary retention. No cross-process stress benchmark, memory usage measurement, timeout enforcement for arbitrarily complex user-supplied objects, or production deployment.
