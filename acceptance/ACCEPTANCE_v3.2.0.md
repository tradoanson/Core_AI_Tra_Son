# ACCEPTANCE v3.2.0 — CI VERIFIED

- Baseline: merged integration contract PR #43, main commit `66eb6cbd56c4aa92b8832c0e8ab42d4faf222619`.
- Scope: v3.2.0 versioned read-only SHADOW integration contract, six synthetic tests, packaging version 3.2.0, independent package smoke, compatibility tests, wheel and Windows EXE.
- Acceptance evidence: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41266072798
- Verified CI commit: `8ad6649c2c6033e28ab8a3ff225d37f3bf2443ba`.
- Result: **SUCCESS, 6/6 jobs** (Python 3.11, 3.12, 3.13; Windows native; wheel; Windows EXE).
- Python tests: 492 discovered; Python 3.11 log reports 492 run, 5 Windows-only skips, 0 failures; Windows native tests run separately.
- CI artifacts: `core-ai-tra-son-wheel-v3.2.0` (45,103 bytes); `core-ai-tra-son-windows-exe-v3.2.0` (11,140,582 bytes). Artifact availability subject to GitHub retention.
- No live VTND/Nhankhau integration or production execution. The contract's caller-supplied `verified` field does not independently authenticate observations.
- **Acceptance decision:** dedicated v3.2.0 CI gate PASS on the stated SHA; PR merge and post-merge main CI are separate subsequent gates.
- Rollback baseline: `b993905cfcbeefd67f6a08cabfb3a975126874e2` (v3.1.0).
