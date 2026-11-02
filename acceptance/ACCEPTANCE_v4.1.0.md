# Core AI Trà Sơn v4.1.0 — Learning Foundation Acceptance

Status: **PENDING CI**. No claim of trained ML or real-system integration.

## Scope
- Deterministic, dependency-free offline learning dataset contract and baseline evaluation.
- Explicit independently verified labels, group-isolated train/validation/test splits.
- Duplicate sample rejection, bounded values, deterministic SHA256 digest.
- MAE, RMSE and nearest-rank P95 absolute error on an explicit split.
- No automatic training, promotion, host reads or writes.

## Required gates
- [ ] Python 3.11/3.12/3.13 full suite and installed smoke PASS.
- [ ] Learning foundation regression tests PASS, including leakage and unverified rejection.
- [ ] Windows native tests PASS.
- [ ] Wheel SHA256 verification and artifact upload PASS.
- [ ] Windows EXE offline self-test and artifact upload PASS.
- [ ] PR CI PASS before merge.
- [ ] Post-merge main CI PASS with artifacts and digests.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v4.1.0.yml

This version measures baseline; it does not claim model improvement. Independent test-set model comparison is planned for subsequent versions.
