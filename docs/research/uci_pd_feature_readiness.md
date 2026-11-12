# UCI PD Feature Readiness and Descriptive Fairness Audit

**Status:** implementation proposed; manual Colab validation pending  
**Scope:** read-only profiling; no model training, fitted preprocessing, or causal inference

## Feature grouping proposal

The audit partitions the 23 contract predictors into:

- **Discrete nominal codes:** `SEX`, `EDUCATION`, `MARRIAGE`, `PAY_0`, and `PAY_2`–`PAY_6`. One-hot encoding is a candidate for a later modeling design because undocumented values must remain distinct and no ordinal distance should be silently assumed.
- **Continuous numeric:** `LIMIT_BAL`, `AGE`, `BILL_AMT1`–`BILL_AMT6`, and `PAY_AMT1`–`PAY_AMT6`. This is a descriptive grouping, not authorization to scale or transform them.

The groups partition the current contract's 23 features. No feature transformation is fitted by this audit.

## Fairness review

The contract flags `SEX`, `EDUCATION`, `MARRIAGE`, and `AGE` for review. The audit reports group counts and observed positive-outcome rates as descriptive diagnostics only. These are not formal fairness metrics, do not establish fairness or unfairness, and do not determine whether these attributes should be used by a future model.

## Blocking issue: feature availability

The source's exact operational observation cutoff and target window remain insufficiently documented. The audit therefore marks feature availability as unresolved. In particular, no predictor is certified as available at a real-world decision time by this profiling step.

## Non-goals

- No category relabeling or collapsing.
- No clipping, winsorization, imputation, scaling, or encoding.
- No feature selection.
- No model training or evaluation.
- No causal effect estimation.
- No production authorization.

## Validation

Run the new unit tests and the audit on the acquired UCI frame in Colab. Persist the resulting report only after reviewing the observed code counts, numeric summaries, and descriptive subgroup outcome rates.
