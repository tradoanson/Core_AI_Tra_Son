# v3.1.0 Modular Core Audit and Acceptance

## Audit baseline
- `core_ai_tra_son/__init__.py` exports CoreAI and Decision without GUI dependency.
- `scripts/windows_shadow_viewer.py` previously owned synthetic `snapshot` business logic and imported Tkinter at module import.
- Python package and GUI were already separately packaged; no wholesale rewrite is warranted.

## Change
- Extract pure synthetic `shadow_snapshot()` into package, retain `scripts.windows_shadow_viewer.snapshot()` wrapper.
- No new network, IPC, real data or host-action capability.
- Test import without Tkinter, backwards-compatible snapshot results, invalid inputs, Windows EXE self-test, >=486 unit tests and Linux 3.11–3.13.

## Limitations
- This does not yet establish a stable public SDK/API or integration contract.
- Windows GUI display on clean machines remains unverified; CI headless EXE smoke is not full UI acceptance.
- Status pending CI; merge only if required gates pass.
