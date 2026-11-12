# Dataset Source Audit — CCI

**Status:** desk research plus local acquisition, structural, semantic, and benchmark-contract validation  \
**Date:** 2026-11-12  \
**Research branch:** `research/dataset-source-audit`  \
**Contract branch:** `feat/uci-benchmark-contract`  \
**Decision scope:** source selection for Data Engine / PD benchmark; not causal identification approval

## 1. Executive decision

Use **UCI Default of Credit Card Clients (UCI dataset 350)** as the first controlled Data Engine and predictive-default (PD) benchmark.

This is an engineering and predictive-benchmark selection only. The dataset is not sufficient, by itself, to estimate the causal effect of increasing a credit limit. It contains an observed credit-limit amount (`LIMIT_BAL`) and six months of repayment/bill/payment information, plus a next-month default outcome. It does not establish a customer-level sequence of credit-limit changes, an intervention timestamp, or a treatment assignment process.

**Causal Engine remains blocked for real-data estimation.** Do not reinterpret a cross-sectional limit amount as a before/after intervention.

## 2. Candidate comparison

| Candidate | Useful content | Main limitation for CCI | Preliminary role |
|---|---|---|---|
| UCI Default of Credit Card Clients | 30,000 Taiwan credit-card clients; credit limit, demographics, repayment status, bill statements, payment amounts, next-month default | No demonstrated longitudinal credit-limit intervention; observation date and treatment assignment are not established | First PD/Data Engine benchmark |
| Home Credit Default Risk | Relational application, bureau, bureau-balance, previous-credit and monthly-history tables | Prediction-oriented application sample; no demonstrated credit-limit intervention history | Possible later relational-ingestion benchmark |
| LendingClub accepted loans | Large historical accepted/funded-loan records, loan amounts, issue dates, borrower features and loan status | Accepted-loan selection; loan amount/funding is not equivalent to a credit-line increase; causal assumptions require separate justification | Possible later loan-origination / vintage-analysis benchmark |

## 3. Source references

1. UCI, **Default of Credit Card Clients**, dataset 350, DOI: https://doi.org/10.24432/C55S3H  
   Official description lists 30,000 clients and variables including amount of credit given, demographics, monthly repayment status, bill statements, payment amounts, and default payment.
2. Home Credit Default Risk competition data: https://www.kaggle.com/c/home-credit-default-risk/data  
   The published data description includes application-level data and relational tables such as bureau, bureau balance, previous applications, and monthly installment/payment history.
3. LendingClub accepted-loan data description (secondary documentation): https://github.com/michelkana/lendingclub/blob/master/CS109aLendingClub_Data.md  
   Describes accepted/funded loans from 2007 to 2018 Q3, with loan-level attributes and status. Treat this as a discovery reference, not an authoritative current distribution or license statement.

UCI's official dataset page lists **CC BY 4.0** and provides the dataset download and citation. Preserve attribution to I-Cheng Yeh and the UCI dataset record; indicate any adaptations. The acquired archive's SHA-256 is recorded below. Do not treat third-party mirrors as canonical.

## 4. UCI variable-level suitability

The published UCI description identifies:

- `LIMIT_BAL`: amount of credit given (NT dollars).
- Demographic fields: `SEX`, `EDUCATION`, `MARRIAGE`, `AGE`.
- Monthly repayment-status fields: `PAY_0`, `PAY_2`–`PAY_6`.
- Bill statement fields: `BILL_AMT1`–`BILL_AMT6`.
- Payment amount fields: `PAY_AMT1`–`PAY_AMT6`.
- Outcome: `default payment next month` (original XLS column label).

### Important temporal and causal restrictions

- The source describes six months of client history from April through September 2005 and a next-month default label.
- `LIMIT_BAL` is an observed credit amount, not a documented treatment event.
- The public description does not provide a before/after limit pair, limit-change date, reason for change, policy assignment, or repeated customer snapshots around a limit intervention.
- The monthly feature suffixes map to April–September 2005; the exact operational prediction cutoff and target observation window remain insufficiently specified for production-timing claims.
- The next-month default label must not enter the feature set.
- The repayment and bill/payment fields require a precise observation cutoff before they can be considered pre-treatment covariates for any hypothetical intervention.

Consequently, this dataset can support an engineering and predictive benchmark, but it does not currently support the CCI target estimand: **effect of a material credit-limit increase on subsequent default risk.**

## 5. Compatibility with the current CCI causal contract

The causal contract expects identifiers `customer_id`, `observation_date`, treatment indicator `treatment_indicator`, before/after limit fields `credit_limit_before` / `credit_limit_after`, and outcomes `default_6m` / `default_12m`.

The UCI source does not establish direct equivalents for these intervention and longitudinal fields. Do not rename `LIMIT_BAL` to `credit_limit_before` or `credit_limit_after`. Do not rename the next-month outcome to `default_6m` or `default_12m`.

A source-specific predictive-benchmark contract is therefore maintained separately. The causal contract remains unchanged.

## 6. Acquisition and structural audit — completed

The user executed the acquisition and read-only audit in Colab on 2026-11-12.

| Evidence | Observed result |
|---|---|
| Original archive | `data/raw/uci_default_credit_card_clients/original_source.zip` |
| SHA-256 | `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602` |
| Archive member | `default of credit card clients.xls` |
| Sheet / header | `Data` / Excel row 2 (`header=1`) |
| Shape | 30,000 rows × 25 columns |
| Missing cells | 0 |
| Duplicate rows | 0 |
| Duplicate IDs | 0 |
| Target | Binary 0/1; 23,364 non-default and 6,636 default |
| Structural quality gates | PASS |

The original archive was not modified. No model training was performed. Raw data is not committed to this repository.

## 7. Semantic audit findings

- UCI's primary variable description documents `EDUCATION` codes 1–4; observed values 0, 5, and 6 are not explained there.
- UCI's primary description documents `MARRIAGE` codes 1–3; observed value 0 is not explained there.
- For repayment status, UCI documents `-1` and delay codes 1–9; observed `-2` and `0` are not explained in the primary description.
- Negative `BILL_AMT*` values were observed. They are preserved; no automatic clipping or winsorization is authorized.
- Preserve original category values until a preprocessing decision is supported and recorded.
- `SEX`, `EDUCATION`, `MARRIAGE`, and `AGE` require fairness review before any deployment-oriented use.

The absence of an official definition is not permission to invent one. Secondary interpretations must remain explicitly labelled as secondary.

## 8. Predictive benchmark contract

A source-specific contract is stored at:

`configs/datasets/uci_credit_default_benchmark_v1.json`

It defines 23 predictors, excludes `ID` from model features, identifies the binary target, records the source DOI/license and archive checksum, preserves undocumented codes, records temporal uncertainty, and explicitly prohibits interpreting this dataset as evidence of credit-limit intervention effects.

A validation record is stored at:

`artifacts/audits/uci_benchmark_contract_validation.json`

The user-reported Colab validation returned **PASS** for archive integrity, source member, schema, missingness, unique identifier, binary target, numeric schema, and contract JSON reload. The record is an execution report supplied by the user; it is not represented as an independently rerun CI result.

## 9. Current gate status

| Gate | Status |
|---|---|
| Candidate discovery | PASS |
| UCI source and license verification | PASS — CC BY 4.0; attribution recorded |
| Local raw file acquired | PASS — Colab |
| Archive integrity / SHA-256 | PASS |
| Actual schema and structural quality audit | PASS |
| Semantic review | COMPLETED — unresolved codes preserved and documented |
| Separate predictive benchmark contract | PASS — user-reported Colab validation |
| Contract versioned on feature branch | PASS |
| Automated repository tests for benchmark contract | PENDING |
| Predictive data pipeline | NOT STARTED |
| Model training | NOT STARTED |
| Causal identification readiness | BLOCKED |

## 10. Next actions

1. Add repository unit tests for the benchmark contract and validate them manually in Colab.
2. Implement a read-only, source-specific loader/validator with explicit schema and provenance checks.
3. Build a predictive split protocol only after temporal semantics and evaluation design are reviewed.
4. Continue searching for longitudinal credit-line data with customer snapshots, limit-change timestamps, treatment assignment/context, and post-intervention outcomes.
5. If no suitable public observational source exists, use a clearly labelled synthetic longitudinal environment to test causal estimators and diagnostics, keeping synthetic evidence separate from empirical claims.

**No causal effect, ATE, CATE, propensity score, or model-performance result is established by this audit.**
