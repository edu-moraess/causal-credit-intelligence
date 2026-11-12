# UCI PD preprocessing protocol

**Protocol:** `uci_credit_default_pd_preprocessing_v1`  
**Scope:** retrospective, research-only predictive benchmark  
**Status:** implementation proposed; manual Colab validation pending

## Transformations

- Nine discrete nominal-code columns are one-hot encoded. Raw codes are preserved; no undocumented category meanings or ordinal distances are inferred.
- Fourteen continuous numeric columns are standardized with `StandardScaler`.
- No clipping, winsorization, automatic feature selection, or imputation is performed.
- Unknown nominal categories at transform time are ignored by the fitted encoder.
- `ID` and `default payment next month` are excluded from the feature matrix.

## Partition discipline

The deterministic stratified 70/15/15 split (seed 42) is created before any fitted transformation. The transformer is fitted only on train. Validation and test are transform-only. The test partition remains sealed for model and threshold selection and is reserved for one final evaluation after those choices are frozen.

## Implementation

`prepare_uci_pd_partitions` implements the train-only fit/transform sequence. It returns train and validation matrices, copied target arrays, the fitted transformer, and feature names. The test partition remains sealed by default: neither its features nor labels are returned or passed through the transformer. Set `release_test=True` only after the model and threshold are frozen. The helper does not train a predictive estimator or calculate model metrics.

## Limitations

The 23 predictors' operational availability remains unresolved and feature leakage remains undetermined. The split is random, not temporal or out-of-time. This protocol does not establish deployment readiness, fairness certification, or causal identification. The causal track remains disabled for this dataset.

## Validation

Automated tests are included. Manual execution in Colab is pending; no CI or successful test result is claimed by this change.
