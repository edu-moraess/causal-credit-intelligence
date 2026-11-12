# UCI Predictive Benchmark — Split Protocol

**Status:** proposed protocol; implementation requires manual Colab validation  
**Scope:** predictive benchmark only; not causal identification and not temporal validation

## Decision

Use a deterministic, stratified random partition with 70% train, 15% validation, and 15% test. The random seed is 42. Stratification is performed on the binary target, preserving the class ratio as closely as integer allocation permits.

This is an engineering benchmark split. The UCI source describes predictors from April–September 2005 and a next-month default label, but does not establish a sufficiently precise operational observation cutoff or exact target window. Therefore this protocol **does not claim temporal, chronological, or out-of-time validation**.

## Isolation and leakage controls

- Partition rows before fitting any learned preprocessing.
- Fit imputers, scalers, encoders, feature selectors, and other learned transformations on the training partition only.
- Apply the frozen transformations to validation and test.
- Use validation for model selection and threshold selection.
- Freeze model and threshold before a single final test evaluation.
- Do not reuse test results to tune features, hyperparameters, or thresholds.
- Exclude `ID` from all model features.
- Exclude `default payment next month` from all model features; it is the target only.
- Preserve original raw values and category codes. No automatic relabeling, clipping, winsorization, or feature engineering is performed by the split module.

## Fairness and deployment restrictions

`SEX`, `EDUCATION`, `MARRIAGE`, and `AGE` require a separate fairness review. The split protocol does not authorize production use, credit decisions, or deployment. A later modeling stage must specify whether demographic variables are included in the primary benchmark and provide sensitivity analyses; that decision is intentionally not made here.

## Implementation boundary

The implementation returns positional row indices and an in-memory manifest. It does not write data files, mutate the source frame, fit transformations, or train models. Split indices are deterministic, disjoint, exhaustive, and target-stratified.

## Validation checklist

- [ ] Config contract and containment tests pass.
- [ ] Deterministic behavior confirmed in Colab.
- [ ] Train/validation/test indices are exhaustive and pairwise disjoint.
- [ ] Target stratification confirmed on the acquired 30,000-row source.
- [ ] Source DataFrame and original ZIP checksums remain unchanged.
- [ ] Full repository test suite passes.
- [ ] No training or fitted preprocessing occurred.
