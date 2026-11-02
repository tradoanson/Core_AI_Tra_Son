# Core AI Trà Sơn v4.7.0 — Learning Audit V1 Acceptance

Status: **PENDING CI**.

## Scope
- Read-only multi-scenario SHADOW audit of baseline, Adaptive V3 and Tiny ML V1.
- Independent dataset digests, deterministic scenario aggregation, baseline-only rejection and regression checks.
- Immutable reports with no model promotion or live system access.
- Scenario datasets must be independently representative before claiming real-world improvement.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites, installed smoke and audit tests PASS.
- [ ] Scenario deduplication, reproducibility, baseline-only rejection and fail-closed tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS and artifacts verified.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.7.0.yml

Passing on synthetic datasets alone is not evidence of production accuracy or general intelligence.
