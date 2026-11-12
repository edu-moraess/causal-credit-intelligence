# UCI PD Retrospective Benchmark — Scope and Training Gate

**Status:** proposed; explicit user scope approval required  
**Dataset:** UCI Default of Credit Card Clients  
**Policy:** `configs/research/uci_pd_retrospective_benchmark_scope_v1.json`

## 1. Decision required before training

The source describes monthly predictor records from April through September 2005 and labels the target "Default payment next month", but it does not provide the exact operational observation cutoff, within-month feature availability timestamps, or an exact calendar target window. The temporal audit therefore marks all 23 predictors as unresolved for operational availability and does not determine whether leakage is present or absent.

This does not make every retrospective experiment impossible. It does limit what the experiment can claim.

## 2. Proposed permitted scope

If explicitly approved, the first PD experiment may be conducted only as a **retrospective predictive benchmark on the supplied historical UCI dataset**.

Permitted research questions:
- Can candidate classifiers discriminate the dataset's recorded positive and negative outcomes?
- How do models compare under the fixed stratified random partition?
- Are predicted probabilities calibrated on the held-out retrospective sample?
- How do errors and descriptive performance vary across reviewed subgroups?

Every result must disclose that:
- the split is random, not chronological;
- no out-of-time or future-period generalization is established;
- feature availability at an operational decision cutoff is unresolved;
- feature-level leakage is not determined;
- no production credit decision is authorized;
- no causal effect of changing a credit limit can be inferred.

## 3. Explicitly prohibited claims

This benchmark must not be presented as:
- a production-ready credit scoring model;
- a temporally validated model;
- evidence of performance on future applicants or future economic periods;
- a causal estimate of the effect of credit-limit changes;
- a fairness certification or deployment approval.

## 4. Training gate

Training remains **not authorized** until the user explicitly approves the retrospective benchmark scope and the following are reviewed:

1. The fixed feature set and unresolved availability/leakage limitations.
2. A preprocessing protocol, with every fitted operation trained on the training partition only.
3. A validation-only model/threshold selection policy.
4. A sealed test-set policy: do not inspect test performance during model or threshold selection; use the test partition once after the model and threshold are frozen.
5. A reporting template that carries the restrictions above into every result.

No training, fitting, transformation, tuning, or test-set inspection is part of this proposal.

## 5. Split and evaluation protocol

The existing 70/15/15 stratified random split with seed 42 remains the proposed reproducible partition. It is not a temporal split. The validation partition may support model and threshold selection after approval. The test partition is reserved for a single final retrospective evaluation after choices are frozen.

## 6. Separate causal research track

The causal track remains blocked on this dataset. It requires a separate longitudinal source with documented treatment assignment or intervention, pre-intervention covariates, treatment timing, and a defined post-intervention outcome. A predictive association from the UCI benchmark must not be converted into a causal claim.

## 7. Decision record

| Decision | Current status |
|---|---|
| Retrospective benchmark scope | Proposed; user approval pending |
| Training | Not authorized |
| Preprocessing | Not authorized |
| Hyperparameter tuning | Not authorized |
| Test-set evaluation | Not authorized |
| Operational deployment | Not authorized |
| Causal estimation from UCI | Unsupported |

The policy is intentionally conservative. Approving the retrospective research scope would authorize planning and execution of that bounded experiment only after the remaining gates are reviewed; it would not authorize production use or causal estimation.
