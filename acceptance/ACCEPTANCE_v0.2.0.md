# Acceptance — Core AI Trà Sơn v0.2.0

Status: **PENDING FINAL CI**. GitHub-only; no physical-machine or production testing.

## Scope
- New `core_ai_tra_son/memory.py`: SQLite-backed ETA adaptive memory.
- Explicit `initialize()`; reads of a missing database return zero state without creating files.
- Learning requires `verified=True`, finite ETA in range and an error <=3600 seconds.
- Separate `namespace` keys isolate project memories.
- Memory persists across object recreation/restarts.
- Existing v0.1.1 decision logic is not integrated with or replaced by memory.

## Tests
- 12 new tests in `tests/test_adaptive_memory_v0_2_0.py`.
- 17 existing unit/safety tests plus release acceptance tests; GitHub Actions requires >=30 discovered tests.
- Python 3.11/3.12/3.13, clean install, offline smoke, static safety.
- Workflow `.github/workflows/release-acceptance-v0.2.0.yml`.
- Evidence URL: https://github.com/tradoanson/Core_AI_Tra_Son/actions/workflows/release-acceptance-v0.2.0.yml
- Final commit SHA, exact CI run URL, conclusions and rollback evidence must be recorded before release tag.

## Security boundaries and limitations
- This module creates and writes only the explicitly supplied SQLite path, after initialization; caller must provide a dedicated path. No automatic access to live application databases.
- Existing file detection checks for the schema marker, but does not authenticate file ownership; do not supply arbitrary or production DB paths.
- No cloud sync, remote calls, trained ML, automatic VTND actions, citizen-record mutations or deployment.
- Schema migrations, multi-process stress and actual application adapters are outside v0.2.0.
