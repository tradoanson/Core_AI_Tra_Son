# Decision Evaluation & Learning Quality v0.7.0

```python
from core_ai_tra_son.decision_quality import DecisionCase, evaluate_quality, rollback_on_degradation
from core_ai_tra_son.decision_learning import DecisionLearningState

holdout = [DecisionCase("fixture-" + str(i),
           {"march_available": 2, "resource_available": True,
            "eta_seconds": 100, "return_buffer_seconds": 300},
           "REVIEW_GATHER") for i in range(8)]
before = DecisionLearningState()
after = DecisionLearningState(gather_adjustment=0.08, return_adjustment=-0.08,
                              gather_samples=4, return_samples=4)
report = evaluate_quality(holdout, after, max_regressions=0, min_delta=0.0)
approved = rollback_on_degradation(after, before, report)
```

Holdout labels must be independently verified and kept separate from training outcomes by the caller. Reports include baseline and adapted accuracy, score delta, case IDs of regressions/improvements and abstentions. At least 8 resolvable cases are needed. The evaluation itself never updates the learner or host.

Policy safety gates are unchanged; quality scores are synthetic-label agreement, not calibrated probabilities. Regression threshold defaults to zero and quality delta to nonnegative. Rollback returns the prior immutable in-memory state; it does not edit SQLite ledger or authenticated checkpoint. Production validation remains future work.
