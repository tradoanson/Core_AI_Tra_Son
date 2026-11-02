# Core AI Trà Sơn v5.0.0 — Learning Pipeline V1 Acceptance

Status: **PENDING CI**.

## Scope
- Single explicit API enforcing verified dataset validation, train-data quality gate and SHADOW benchmark in order.
- Quality failure returns baseline and skips model training/evaluation.
- Read-only offline report; no automatic promotion, persistence, host access or live system integration.
- Standalone legacy learning functions remain callable: callers must opt into the new pipeline to enforce the quality gate.
- Dataset digests guard consistency but do not provide independent label authenticity.

## Mandatory gates
- [ ] Python 3.11/3.12/3.13 full suites and end-to-end pipeline tests PASS.
- [ ] Quality-failure short circuit, independent holdout, no promotion and determinism PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE builds, SHA256 and artifact upload PASS.
- [ ] PR six-job CI PASS before merge.
- [ ] Post-merge main six-job CI PASS.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v5.0.0.yml
