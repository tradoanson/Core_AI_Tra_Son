# ACCEPTANCE v3.3.0 — CODE GATES PASS, RELEASE PENDING

## Scope and baseline
- Previous baseline: v3.2.0 integration contract (protocol version remains `3.2.0` for backward compatibility).
- v3.3.0 diagnostics introduced by PR #46, merged to main as `4eadcfcbc44dae6f623319be7942271af9e9f802`.
- Packaging version finalized by PR #47, merged to main as `cb6ed392c2703a9a9ed00259c8f36aa22c44c1fd`.
- Nine new synthetic diagnostic tests (fail-closed malformed requests, metadata and caller verification type); no live integration.
- No independent attestation: caller-provided `verified=True` is not proof of trustworthy data. `independently_verified=False` is explicit.
- No GUI import or execution from the diagnostics module; all responses remain SHADOW.
- Rollback target: main commit `b7a197d332c9226921cb0c4834c6aa63fba34512` (v3.2.0 post-merge).

## Verified prior evidence
- PR #47 branch head `22c1d363f213aa4904653515ff471cb00c669029`.
- Generic versioned verification: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41295375476 — SUCCESS (Python 3.11/3.12/3.13).
- Legacy v3.2.0 contract gate: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41295375471 — SUCCESS (6/6 jobs, including wheel and Windows EXE).
- The above legacy gate publishes v3.2.0-named artifacts and **does not** certify v3.3.0 artifact names.

## Dedicated v3.3.0 CI evidence (code snapshot)
- Verified code/workflow SHA: `4f217b059778b2ce6dcf3c8cb04a5e20353acc7f`.
- Workflow run: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41373555169 — **SUCCESS, 6/6 jobs**.
- Python 3.11: 501 tests, 5 Windows-only skips, zero failures; v3.2 contract 6 tests and v3.3 diagnostics 9 tests PASS. Python 3.12/3.13 jobs PASS.
- Offline installed-package smoke: version 3.3.0, production_integrated=false.
- Wheel artifact: `core-ai-tra-son-wheel-v3.3.0` (GitHub artifact ZIP 45,740 bytes); wheel SHA256 `4bac73026fe442001ad1095a0bdce376dd608fa1dde60f3420455af632b9b904`.
- Windows EXE artifact: `core-ai-tra-son-windows-exe-v3.3.0` (GitHub artifact ZIP 11,140,967 bytes); EXE SHA256 `43463e1fcfdfe06d73d7f393dffda1e71d47fe39002928795e091bed161f8d92`.
- Windows EXE offline self-test and Windows native locking tests PASS. Artifact availability subject to retention.
- This run predates documentation-only commits; final branch head and post-merge main CI are separate gates.

## Required before certification
- Dedicated v3.3.0 workflow: Python 3.11–3.13, >=501 discovered tests, isolated smoke, v3.2 contract compatibility, v3.3 diagnostics, Windows native tests, wheel SHA256 and Windows EXE self-test.
- Record dedicated workflow run URL, exact head SHA, test counts, job results, artifact names and checksums.
- Merge only if all required jobs PASS; rerun the dedicated gate on main after merge.
- Tag/release `v3.3.0` and attach/check artifact hashes only when supported and verified; never infer them from a green tick.
- CI is not evidence of production integration or physical-device operation.

## Current decision
CODE ACCEPTANCE PASS on the recorded SHA. Final branch head CI, post-merge main CI, immutable tag/release and final artifact handover remain PENDING.
