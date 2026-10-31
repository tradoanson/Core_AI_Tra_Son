# Paired Quality Gates v0.9.0

The one-sided exact sign test evaluates whether adapted decisions improve more often than regress relative to the baseline on the same holdout. Default at least eight changed decisions, alpha=0.05, and upstream quality report PASS. Zero changed decisions yields INSUFFICIENT_EVIDENCE. Labels and case independence must be independently validated; repeated/dependent fixtures can invalidate statistical interpretation. Never auto-deploy or resume learning based solely on this test.
