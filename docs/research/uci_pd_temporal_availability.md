# UCI PD Temporal Availability and Leakage Audit

**Status:** implementation proposed; manual Colab validation pending  
**Branch:** `audit/uci-temporal-availability`  
**Scope:** source-temporal mapping and conservative availability assessment; read-only

## 1. Purpose

This audit records what the primary UCI documentation establishes about the time reference of the benchmark predictors and separates that evidence from what remains unknown about operational availability.

It is not a row-level timestamp audit. The distributed UCI table contains no per-customer observation timestamp, statement-close timestamp, feature publication timestamp, or model decision timestamp.

## 2. Primary-source temporal evidence

The UCI dataset description identifies monthly repayment records from April through September 2005. It maps `PAY_0` to September and `PAY_6` to April. It describes bill statement amounts and previous payment amounts over the same monthly period, also in reverse chronological suffix order. The response is labelled **Default payment next month**.

Primary reference:

- UCI Machine Learning Repository, *Default of Credit Card Clients*, dataset 350: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- DOI: https://doi.org/10.24432/C55S3H

The source documents calendar-month references, but does not provide the exact operational observation cutoff, the within-month measurement/release times, a per-record as-of date, or an exact calendar target window. Therefore, this audit does not assign October 2005 as a verified target window.

## 3. Feature-level temporal map

| Feature group | Fields | Documented temporal reference | Operational availability |
|---|---|---|---|
| Credit amount | `LIMIT_BAL` | Point-in-time amount; no as-of date | Unresolved |
| Demographics | `SEX`, `EDUCATION`, `MARRIAGE`, `AGE` | No reference/measurement date | Unresolved |
| Repayment status | `PAY_6` to `PAY_0` | April to September 2005 | Unresolved within each month |
| Bill statements | `BILL_AMT6` to `BILL_AMT1` | April to September 2005 | Unresolved within each month |
| Previous payments | `PAY_AMT6` to `PAY_AMT1` | April to September 2005 | Unresolved within each month |

The month mapping is recorded explicitly in `configs/audits/uci_credit_default_temporal_availability_v1.json`. It is source metadata, not evidence that each value was available to a lender at a specific time.

## 4. Leakage assessment

The audit deliberately distinguishes three conclusions:

1. **Documented:** calendar month references exist for the monthly feature families.
2. **Unknown:** exact operational cutoff and within-month availability timestamps are absent.
3. **Not established:** neither the presence nor the absence of leakage can be certified from this source documentation alone.

Consequently, every predictor remains marked `availability_at_operational_cutoff = unresolved` and `potential_leakage_status = not_determined`. This is not a finding that all features leak; it is a finding that the available evidence cannot certify their availability at a real-world decision time.

## 5. Consequences for evaluation

- The existing 70/15/15 stratified random split remains a reproducible **random benchmark partition**, not temporal or out-of-time validation.
- No temporal holdout can be constructed from this dataset because there are no customer-level observation dates or repeated dated snapshots.
- The benchmark may eventually support a clearly labelled retrospective predictive experiment, but the model's prediction-time interpretation must remain limited by the source's timing documentation.
- Do not use a good random-split score as evidence of production readiness or future-period generalization.

## 6. Gate decision

| Gate | Status |
|---|---|
| Source calendar-month mapping | Documented |
| Exact operational observation cutoff | Unresolved |
| Within-month feature availability | Unresolved |
| Exact target calendar window | Unresolved |
| Feature-level leakage absence | Not established |
| Temporal/out-of-time validation | Unsupported by this dataset |
| Model training authorization | Blocked pending scope decision |
| Production use | Not authorized |

## 7. Non-goals

- No imputation, encoding, scaling, clipping, winsorization, or feature selection.
- No fitting, model training, tuning, or model evaluation.
- No causal estimation.
- No assertion that a feature is definitely leaked or definitely safe.
- No alteration of the UCI source or the existing predictive split protocol.

## 8. Manual validation in Colab

After checking out this branch and installing the project with test and benchmark extras:

```bash
python -m pip install -e ".[test,benchmark]"
python -m pytest -v
```

Then run the read-only audit against the acquired archive. The expected report has 23 features, zero certified as operationally available, all 23 unresolved, no leakage conclusion, and no training or frame mutation. Persist a validation artifact only after the user reports the actual Colab result.

