# Core AI Trà Sơn v3.9.0 — Acceptance

Status: **PENDING CI**. No PASS is claimed before verified GitHub checks.

## Scope
- Read-only SHADOW diagnostics reject bytes and bytearray observation values exceeding 4096 bytes.
- Existing integration protocol v3.2 and previous bounded diagnostics remain compatible.
- Package, installed smoke and acceptance version aligned to 3.9.0.
- No real-system integration.

## Required gates
- [ ] Python 3.11, 3.12, 3.13 full offline suite and installed smoke PASS.
- [ ] v3.9.0 binary bounds and prior safety regression tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel SHA256 verification and artifact upload PASS.
- [ ] Windows EXE offline self-test and artifact upload PASS.
- [ ] PR six-job CI PASS; merge only after required checks.
- [ ] Post-merge main six-job CI PASS and artifact digests available.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v3.9.0.yml

GitHub-only acceptance does not establish a formal GitHub Release or production deployment.
