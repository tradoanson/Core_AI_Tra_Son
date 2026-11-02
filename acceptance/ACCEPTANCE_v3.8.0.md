# Core AI Trà Sơn v3.8.0 — Acceptance

Status: **PENDING CI**. The workflow run is the authoritative acceptance evidence.

## Scope
- Fail-closed bounded integration metadata (project and contract version length <=128).
- SHADOW-only diagnostics; no real-system integration, no independent verification claim.
- Existing v3.2 protocol and v3.7 behavior preserved.
- Package version, smoke and acceptance assertions: 3.8.0.

## Required gates
- [ ] Python 3.11, 3.12 and 3.13 offline test suite and installed smoke PASS.
- [ ] Dedicated v3.8.0 metadata regression tests PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel build, SHA256 verification and artifact upload PASS.
- [ ] Windows EXE build, offline self-test and artifact upload PASS.
- [ ] Six-job PR workflow PASS; merge only after all mandatory checks.
- [ ] Post-merge main workflow PASS and artifact digests recorded.

Evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v3.8.0.yml

GitHub-only acceptance does not imply a formal tag/release or production deployment.
