# Core AI Trà Sơn v4.2.0 — Adaptive Learning V3 Acceptance

Status: **PENDING CI**.

## Scope
- Offline bounded deterministic ETA bias learning using verified train split only.
- Independent evaluation on requested validation/test split with MAE, RMSE, P95 and improvement percentage.
- No model promotion, host access, production integration or learning from test labels.
- Preserve v4.1 dataset integrity and existing v3.2 integration contract.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suite, smoke and adaptive tests PASS.
- [ ] Test-label isolation, reproducibility, bounded bias and no mutation tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, offline self-test, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS and artifacts verified.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.2.0.yml

Demonstrating improvement on a synthetic example is not evidence of production improvement. Future model promotion requires separately approved quality gates.
