# Core AI Trà Sơn v4.0.0 — Acceptance

Status: **PENDING CI**. A PASS requires verified GitHub workflow evidence.

## Scope
- Nonrecursive, bounded nested observation diagnostics with max container depth 8.
- Preserve v3.2 integration protocol, prior bounds and SHADOW-only operation.
- Package metadata, installed smoke and acceptance assertions aligned to 4.0.0.
- No live integration, no production data, no autonomous host action.

## Mandatory gates
- [ ] Python 3.11, 3.12, 3.13 complete offline tests and installed smoke PASS.
- [ ] v4.0.0 nested depth and prior regression tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel built and SHA256 verified.
- [ ] Windows EXE built and offline self-test PASS.
- [ ] PR six-job CI PASS; merge only after required checks.
- [ ] Post-merge main six-job CI PASS and artifact SHA256 evidence available.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.0.0.yml

GitHub-only acceptance does not establish a formal tag/release or live-system integration.
