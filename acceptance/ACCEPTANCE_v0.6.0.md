# v0.6.0 — Adaptive Decision Learning

Status: PENDING GitHub Actions and merge verification.

Scope: immutable in-memory verified-only outcome learner, fixed maximum score adjustment +/-0.08 per review option, +0.02/-0.02 updates per verified positive/negative label, max 1,000,000 observations per option. No learned adjustment to WAIT, blocked options, verification gates, resource eligibility or action execution.

Acceptance: >=140 tests, clean install, Python 3.11–3.13, offline smoke, static safety and regression; unverified outcomes do not learn; malicious learning state fails closed; repeatable parallel evaluation.

Limitations: Verification is a trusted caller-supplied boolean, not independently authenticated evidence. This is bounded feedback-based preference adjustment, not statistical ML or proven decision quality. State is immutable and caller-owned, not automatically persisted. No production integration, no host execution, no machine testing.
