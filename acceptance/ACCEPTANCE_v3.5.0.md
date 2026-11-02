# Core AI Trà Sơn v3.5.0 — Acceptance record

Status: **PASS — GitHub-only acceptance**, verified on main commit `86ef87e9c25ea92a6049b885ba97e32e29fdd431`. Formal tag/release remains unverified.

## Scope
- Base main commit before acceptance: `35936089b58e06c4123f8f70dd0d9a6275427198`.
- Implementation PR #51 merged. Package metadata reports 3.5.0.
- Read-only SHADOW diagnostics; no production integration or real personal data.
- Existing integration contract protocol version remains 3.2.0 for compatibility.

## Required evidence
- [x] Dedicated workflow `.github/workflows/release-acceptance-v3.5.0.yml` completes 6/6 jobs.
- [x] Python 3.11, 3.12, 3.13 offline tests and isolated smoke PASS.
- [x] v3.4/v3.5 diagnostic regressions PASS.
- [x] Windows native tests PASS.
- [x] Wheel and Windows EXE build and self-test PASS.
- [x] Artifact SHA256 and run URL recorded.
- [x] PR merged only after all required gates PASS.
- [x] Post-merge CI on main PASS.
- [ ] Tag/release publication verified separately before calling this a formal release.

## Limits
CI is not evidence of a live deployment, a real Windows desktop session, or a real VTND/Nhân Khẩu integration. No such integration is authorized.

## Verified evidence (2026-11-02)
- Implementation PR: https://github.com/tradoanson/Core_AI_Tra_Son/pull/51 (merged).
- Acceptance PR: https://github.com/tradoanson/Core_AI_Tra_Son/pull/52 (merged).
- Post-merge six-job CI: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41384442609 — SUCCESS 6/6.
- Python 3.11/3.12/3.13, Windows native, wheel, Windows EXE: all six jobs SUCCESS.
- Windows EXE artifact ID 13115225224, archive SHA256 `2cd0919acbaef92d7e300df4122b1abd5563e0bd7cf448f2296935c803e27d46`.
- Wheel artifact ID 13115115990, archive SHA256 `c77546ce1d7ee15da92f719b0a0850f7366415cacd6809a0f431d0035618d829`.
- The two digests above identify GitHub artifact archives, not necessarily the individual EXE/wheel binaries.
- This record was appended after the successful run; evidence-only documentation change requires its own CI check before merge.
