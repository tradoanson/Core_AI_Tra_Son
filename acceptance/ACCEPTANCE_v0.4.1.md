# Core AI Trà Sơn v0.4.1 — Reasoning Validation & Calibration

Status: PENDING final GitHub Actions verification and merge.

Scope: deterministic synthetic benchmark, march availability/capacity contradiction detection, confidence-bin agreement diagnostics, repeated and concurrent consistency.

Gates: >=90 regression and new tests, clean install, offline smoke, Python 3.11/3.12/3.13, static safety. Reference suite contains 12 synthetic labelled scenarios, not production observations.

Confidence remains an input-completeness heuristic, NOT a calibrated probability. Benchmark agreement against manually specified expected statuses cannot establish real-world predictive calibration, precision, recall or safety. Report confidence-bin agreement as a diagnostic only.

SHADOW only; no host execution, no real citizen data, no real-machine testing.
