# v0.4.0 Reasoning Engine acceptance

Status: PENDING final GitHub Actions and merge.

Scope: pure deterministic SHADOW multi-signal VTND reasoning with verified march, ETA, return buffer, resource availability and optional memory context. No host execution.

Acceptance: >=75 tests, Python 3.11/3.12/3.13, clean install and offline smoke; malformed/unverified/unknown signals fail closed; bounded confidence; explainable reason codes and allowlisted evidence; deterministic parallel decisions; no network or file writes.

Confidence is a deterministic completeness heuristic (0.6 base, +0.1 per validated optional signal, max 0.9), NOT a statistically calibrated probability. Memory does not increase confidence. No automated action, no production integration and no real machine testing.
