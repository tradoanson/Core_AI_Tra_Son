# Holdout Leakage v1.2.0

Caller-provided verified DecisionCase sequences are hashed in memory and checked for duplicate canonical signals, repeated IDs, and cross-split duplicates. No raw signals are persisted. This is an exact structural check, not semantic near-duplicate detection, independent data sourcing, or statistical independence certification.
