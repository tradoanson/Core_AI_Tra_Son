# Core AI Trà Sơn v3.7.0 — Acceptance

Status: **PENDING CI**. Never mark PASS without a successful run on the exact commit.

## Scope
- SHADOW-only read-only diagnostics; top-level list/tuple/dict observation values limited to 256 elements.
- Existing v3.2 integration protocol preserved; no production integration.
- Python package, installed smoke test and release assertions aligned to 3.7.0.

## Mandatory gates
- [ ] Python 3.11, 3.12, 3.13 complete tests and installed smoke PASS.
- [ ] v3.7.0 regression plus previous safety suites PASS.
- [ ] Windows native tests PASS.
- [ ] Wheel built, verified and artifact uploaded.
- [ ] Windows EXE built, offline self-test PASS and artifact uploaded.
- [ ] Dedicated six-job CI PASS on PR head; merge after PASS.
- [ ] Post-merge dedicated six-job CI PASS on main.
- [ ] Artifact archive digests recorded in GitHub run.

Authoritative evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v3.7.0.yml

This is a GitHub-only acceptance, not a live deployment or a formal release tag.
