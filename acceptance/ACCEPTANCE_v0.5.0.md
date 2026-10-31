# v0.5.0 — Advanced Reasoning acceptance

Status: PENDING final GitHub Actions and merge.

SHADOW-only, predefined bounded options WAIT, REVIEW_GATHER, REVIEW_RETURN. Fixed, explainable policy scores with deterministic tie-break by option ID. Ranking only after v0.4.1 verified signal gate; contradictions and unknown options fail closed. All outputs are recommendations; action_executed always false.

Required: >=105 tests, clean install, Python 3.11–3.13, regression, static safety, parallel deterministic ranking, serialization, no personal data in results.

Scores are heuristic policy priorities, not statistical probabilities, learned utilities or calibrated risk. No real-world deployment or production integration.
