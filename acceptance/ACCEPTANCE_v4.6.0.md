# Core AI Trà Sơn v4.6.0 — SHADOW Benchmark V1 Acceptance

Status: **PENDING CI**.

## Scope
- Reproducible read-only synthetic/offline benchmark comparing baseline, Adaptive V3 and Tiny ML V1.
- Train on verified train split only, evaluate untouched test split with MAE and governance P95 gates.
- Return model recommendation without activation, promotion or host IO.
- Preserve all prior version APIs and safety limits.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites, installed smoke and benchmark tests PASS.
- [ ] Holdout isolation, no promotion, deterministic results and leakage tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS and artifacts verified.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.6.0.yml

Synthetic benchmark outcomes cannot establish real-world model accuracy. Quality recommendations are not deployments.
