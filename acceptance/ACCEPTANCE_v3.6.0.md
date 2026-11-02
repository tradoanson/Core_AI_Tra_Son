# Core AI Trà Sơn v3.6.0 — Acceptance

Status: **PENDING CI**. No PASS is claimed before the actual workflow run.

## Scope
- SHADOW-only, read-only diagnostics: reject observation text longer than 4096 characters.
- Preserve v3.2 integration protocol and prior diagnostic field/key limits.
- Package version, installed smoke test, release acceptance test: 3.6.0.
- No live integration or real data.

## Required gates
- [ ] Python 3.11, 3.12, 3.13 full offline tests and installed smoke.
- [ ] Dedicated v3.6.0 text-bound regression.
- [ ] Windows native tests.
- [ ] Wheel build and SHA256 verification.
- [ ] Windows EXE build and offline self-test.
- [ ] 6/6 workflow jobs SUCCESS on PR head.
- [ ] Merge only after required gates PASS.
- [ ] Post-merge main CI SUCCESS, artifact evidence recorded.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v3.6.0.yml

This record documents acceptance criteria; the GitHub workflow run is the authoritative pass/fail evidence.
