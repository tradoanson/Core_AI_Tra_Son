# Core AI Trà Sơn v4.5.0 — Model Governance V1 Acceptance

Status: **PENDING CI**.

## Scope
- Pure deterministic model quality decisions: minimum independent sample count, MAE improvement threshold and P95 regression cap.
- Fail-closed input and policy validation, explicit baseline fallback and drift-triggered rollback recommendation.
- No model activation, deployment, persistence, host access or real-system integration.
- Governance is a decision API; it cannot establish independent authenticity of reported metrics.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites, installed smoke and governance tests PASS.
- [ ] Quality thresholds, invalid reports, tail regression and rollback tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS and artifacts verified.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.5.0.yml
