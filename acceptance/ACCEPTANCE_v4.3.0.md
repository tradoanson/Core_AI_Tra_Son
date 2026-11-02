# Core AI Trà Sơn v4.3.0 — Tiny ML V1 Acceptance

Status: **PENDING CI**.

## Scope
- Offline CPU-only dependency-free bounded linear residual learner on verified training split.
- Explicit holdout evaluation with MAE, RMSE, P95 and baseline comparison.
- No training on test labels, no automatic promotion, no host integration.
- Existing v4.1 dataset and v4.2 adaptive modules retained.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites, installed smoke and Tiny ML tests PASS.
- [ ] Reproducibility, test isolation, bounded parameters and invalid input tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS and artifacts verified.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.3.0.yml

Synthetic holdout improvement does not imply real-world model quality. No trained model is promoted for operational decisions.
