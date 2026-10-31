# v0.7.0 — Decision Evaluation & Learning Quality

Status: PENDING GitHub Actions and merge verification.

Scope: compare unchanged policy baseline and bounded adapted recommendations against 8..512 caller-verified holdout cases; track exact accuracy, improvements, regressions and abstentions. Fail closed on insufficient evidence. Return prior immutable state on a degraded quality report; no host or storage mutation.

Acceptance: >=240 tests, clean install, Python 3.11/3.12/3.13, regression detection, threshold controls, no evaluation/training leakage within the function, deterministic results, safety policy intact, SHADOW only.

Limits: labels and train/holdout separation are caller-attested, not independently proven; synthetic fixtures are not real-world quality evidence. This rollback is a pure in-memory selection of a prior state, NOT persistent database/checkpoint rollback. Reusing training examples in holdout can inflate accuracy. The acceptance gate is an algorithmic contract, not measured production benefit.
