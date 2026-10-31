# Decision Quality & Safety Validation v0.5.1

Safety changes:
- REVIEW_GATHER now requires explicit verified `resource_available=True`, not merely absence of a negative resource signal.
- REVIEW_RETURN is blocked when `resource_available=False`, even if ETA is due; incomplete ETA/buffer also blocks it.
- Each ranked alternative explains eligibility or blocking; the top-level explanation identifies the selected option and its score.
- All-blocked option lists return UNRESOLVED without a selected action.
- Tests cover ETA exactly equal to buffer, one second beyond buffer, conflicting capacity, missing resource, memory bias, option permutation and concurrent stability.

Trade-off: Conservative unknown-resource handling can increase WAITING decisions but avoids treating missing evidence as positive confirmation. Policy scores are not calibrated probabilities. The engine is advisory SHADOW only.
