# Core AI Trà Sơn v4.9.0 — Learning Data Quality V1 Acceptance

Status: **PENDING CI**.

## Scope
- Read-only verified training data quality gate with bounded absolute residuals and median absolute deviation outlier detection.
- Fail-closed malformed/unverified input and invalid policies; explicit insufficient sample rejection.
- Does not alter datasets, train, promote, write to host, or integrate real systems.
- Advisory gate only: callers must explicitly enforce the returned accepted flag. Robust statistics do not prove data authenticity.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites, installed smoke and data quality tests PASS.
- [ ] Anomaly fraction, policy bounds, unverified rejection and determinism tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.9.0.yml
