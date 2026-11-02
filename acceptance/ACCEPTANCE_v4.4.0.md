# Core AI Trà Sơn v4.4.0 — Model Memory V1 Acceptance

Status: **PENDING CI**.

## Scope
- Immutable in-memory record ledger for model evaluation events, versions and dataset digests.
- SHA256 chained records with deterministic canonical encoding.
- Idempotent replay by event ID; reject conflicting duplicates, malformed events and tampering.
- Bounded memory; no file writes, host access, model auto-promotion or real-system integration.
- Does not claim durable persistence or independent authenticity; persistence is separate future work.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites, installed smoke and memory tests PASS.
- [ ] Tamper, replay, invalid metric, hash-chain and immutability tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS and artifacts verified.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.4.0.yml
