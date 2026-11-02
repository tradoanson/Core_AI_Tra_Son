# Core AI Trà Sơn v4.8.0 — Learning Robustness V1 Acceptance

Status: **PENDING CI**.

## Scope
- Offline deterministic cross-scenario gate: a single model must satisfy improvement and worst-case regression thresholds on all independent holdouts.
- Reject duplicate scenario digests, invalid/unverified examples, invalid policy and insufficient samples.
- Fail closed to baseline; never promote, write to host, or integrate real systems.
- This checks cross-scenario stability, not adversarial security, real-world noise resilience or drift detection.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites and robustness tests PASS.
- [ ] Reproducibility, scenario deduplication and fail-closed tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.8.0.yml
