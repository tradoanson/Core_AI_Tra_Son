# Core AI Trà Sơn v3.5.0 — Acceptance record

Status: **PENDING**. This document is not a PASS certificate.

## Scope
- Base main commit before acceptance: `35936089b58e06c4123f8f70dd0d9a6275427198`.
- Implementation PR #51 merged. Package metadata reports 3.5.0.
- Read-only SHADOW diagnostics; no production integration or real personal data.
- Existing integration contract protocol version remains 3.2.0 for compatibility.

## Required evidence
- [ ] Dedicated workflow `.github/workflows/release-acceptance-v3.5.0.yml` completes 6/6 jobs.
- [ ] Python 3.11, 3.12, 3.13 offline tests and isolated smoke PASS.
- [ ] v3.4/v3.5 diagnostic regressions PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel and Windows EXE build and self-test PASS.
- [ ] Artifact SHA256 and run URL recorded.
- [ ] PR merged only after all required gates PASS.
- [ ] Post-merge CI on main PASS.
- [ ] Tag/release publication verified separately before calling this a formal release.

## Limits
CI is not evidence of a live deployment, a real Windows desktop session, or a real VTND/Nhân Khẩu integration. No such integration is authorized.
