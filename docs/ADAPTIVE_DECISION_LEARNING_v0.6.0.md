# Adaptive Decision Learning v0.6.0

```python
from core_ai_tra_son.decision_learning import DecisionLearner, DecisionLearningState
from core_ai_tra_son.advanced_reasoning import AdvancedReasoner

learner = DecisionLearner()
state = DecisionLearningState()
state = learner.observe(state, "REVIEW_GATHER", successful=True, verified=True)
decision = AdvancedReasoner().rank(
    {"march_available": 2, "resource_available": True},
    verified=True, options=["WAIT", "REVIEW_GATHER"], learning_state=state)
print(decision.to_dict())
```

Learning adjusts only eligible human-review recommendation scores; each verified positive outcome adds 0.02, negative subtracts 0.02, clipped to +/-0.08. WAIT never learns. Invalid or foreign state is rejected. Missing verification produces no update.

This module does not automatically verify outcome provenance or persist state. The caller must provide verified outcomes, own any storage and keep data privacy-reviewed. No production integration or automatic actions. SHADOW only.

Fixed policy scores and feedback adjustments are not calibrated probabilities. Safety checks remain the authority.
