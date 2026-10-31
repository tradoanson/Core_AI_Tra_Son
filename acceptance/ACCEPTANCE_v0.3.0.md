# v0.3.0 Micro Agent Engine — GitHub-only acceptance

Status: PENDING final workflow and merge verification.

Components: observer sanitization, existing CoreAI reasoner, optional caller-supplied Adaptive Memory snapshot, safety gate and structured decision record. No network, disk writes, host APIs, action execution or persistent audit log.

Required checks:
- Unverified observations -> UNRESOLVED; valid empty march -> WAITING; available march -> REVIEW only.
- Invalid input rejected; no personal record values appear in agent output.
- Foreign/invalid memory state rejected; verified VTND memory context can be attached to the recommendation.
- Deterministic JSON-serializable decision output with action_executed=False.
- v0.1.1/v0.2.0/v0.2.1 regressions and >=50 tests across Python 3.11/3.12/3.13.
- Clean install and offline smoke.

Limitations: Memory context does not independently validate SQLite provenance; caller must supply trusted verified state. Agent does not perform ETA scheduling or execute actions. Decision logging is returned to caller; no persistent logs, avoiding personal-data leakage. No integration with production applications.
