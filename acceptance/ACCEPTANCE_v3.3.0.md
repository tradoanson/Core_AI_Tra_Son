# ACCEPTANCE v3.3.0 — PENDING FINAL GATES

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

## Required before certification
- Dedicated v3.3.0 workflow: Python 3.11–3.13, >=501 discovered tests, isolated smoke, v3.2 contract compatibility, v3.3 diagnostics, Windows native tests, wheel SHA256 and Windows EXE self-test.
- Record dedicated workflow run URL, exact head SHA, test counts, job results, artifact names and checksums.
- Merge only if all required jobs PASS; rerun the dedicated gate on main after merge.
- Tag/release `v3.3.0` and attach/check artifact hashes only when supported and verified; never infer them from a green tick.
- CI is not evidence of production integration or physical-device operation.

## Current decision
PENDING: dedicated v3.3.0 acceptance and post-merge release evidence have not yet been verified.
