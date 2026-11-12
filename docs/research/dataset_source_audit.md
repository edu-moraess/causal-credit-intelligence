# Dataset Source Audit — CCI

**Status:** preliminary desk research; no dataset downloaded or inspected locally  
**Date:** 2026-11-12  
**Branch:** `research/dataset-source-audit`  
**Decision scope:** source selection for Data Engine / PD benchmark; not causal identification approval

## 1. Executive decision

Use **UCI Default of Credit Card Clients (UCI dataset 350)** as the first candidate for a controlled Data Engine and predictive-default (PD) benchmark, subject to a fresh local acquisition audit and license/attribution verification.

This is a **provisional engineering selection only**. The dataset is not sufficient, by itself, to estimate the causal effect of increasing a credit limit. It contains a credit-limit amount (`LIMIT_BAL`) and six months of repayment/bill/payment information, plus a next-month default outcome. The available description does not establish a customer-level sequence of credit-limit changes, an intervention timestamp, or a treatment assignment process.

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

Before acquisition, verify the current official source, terms/license, attribution requirements, file checksum, dataset version, and permitted use. Do not treat third-party mirrors as canonical.

## 4. UCI variable-level suitability

The published UCI description identifies:

- `LIMIT_BAL`: amount of credit given (NT dollars).
- Demographic fields: `SEX`, `EDUCATION`, `MARRIAGE`, `AGE`.
- Monthly repayment-status fields: `PAY_0`, `PAY_2`–`PAY_6`.
- Bill statement fields: `BILL_AMT1`–`BILL_AMT6`.
- Payment amount fields: `PAY_AMT1`–`PAY_AMT6`.
- Outcome: `default.payment.next.month`.

### Important temporal and causal restrictions

- The source is described as a set of client records with monthly history and a next-month default label.
- `LIMIT_BAL` is an observed credit amount, not a documented treatment event.
- The available public description does not provide a before/after limit pair, limit-change date, reason for change, policy assignment, or repeated customer snapshots around a limit intervention.
- The monthly feature suffixes need to be mapped carefully to their actual months. Do not infer a treatment date merely from column order.
- The next-month default label must not enter a feature set used to predict or explain the same outcome.
- The repayment and bill/payment fields require a precise observation cutoff before they can be considered pre-treatment covariates for any hypothetical intervention.

Consequently, this dataset can support an engineering and predictive benchmark after validation, but it does not currently support the CCI target estimand:
**effect of a material credit-limit increase on subsequent default risk.**

## 5. Compatibility with the current CCI contract

The current contract expects identifiers `customer_id`, `observation_date`, treatment indicator `treatment_indicator`, before/after limit fields `credit_limit_before` / `credit_limit_after`, and outcomes `default_6m` / `default_12m`.

The UCI source description does not establish direct equivalents for:
- a stable customer identifier suitable for longitudinal linkage;
- an observation/intervention date;
- treatment indicator;
- pre-intervention limit;
- post-intervention limit;
- six- and twelve-month default outcomes.

Do not rename `LIMIT_BAL` to `credit_limit_before` or `credit_limit_after`. Do not rename the next-month outcome to `default_6m` or `default_12m`. Those would create false semantic equivalences.

A source-specific adapter and a separate predictive-benchmark contract will be needed. Keep the causal contract unchanged until a suitable longitudinal source is identified.

## 6. Acquisition and audit gate

No acquisition was performed as part of this desk audit. When explicitly run in Colab, the acquisition workflow must:

1. Download only from the verified canonical source.
2. Preserve the original file unchanged under `data/raw/<source-id>/`.
3. Record source URL, retrieval timestamp (UTC), declared dataset/version, license/terms reference, original filename, byte size, and SHA-256.
4. Store extracted/normalized copies outside the raw directory.
5. Inspect archive contents before extraction and reject unexpected paths or file types.
6. Produce a data dictionary and structural profile without fitting models.
7. Keep raw data out of Git unless repository policy and the source license explicitly permit it.

Required evidence before marking the dataset acquired:
- source page and license/terms captured;
- archive/file checksum;
- file inventory;
- row/column counts from the actual local file;
- duplicate and missingness profile;
- raw-to-canonical mapping with explicit unmapped fields;
- temporal semantics review.

## 7. Current gate status

| Gate | Status |
|---|---|
| Candidate discovery | PASS — desk research only |
| Provisional PD/Data Engine candidate | SELECTED — UCI, pending acquisition audit |
| Canonical source and license verification at acquisition | PENDING |
| Local raw file acquired | NOT RUN |
| File integrity / SHA-256 | NOT RUN |
| Actual schema and data-quality audit | NOT RUN |
| Source-to-CCI mapping | BLOCKED pending inspection |
| PD benchmark readiness | NOT READY |
| Causal identification readiness | BLOCKED |

## 8. Next actions

1. Acquire UCI dataset only after verifying the official download and license/attribution terms.
2. Run a read-only acquisition and structural audit in Colab; no model training.
3. Add a source-specific predictive benchmark contract rather than weakening the causal contract.
4. Continue searching for longitudinal credit-line data with customer snapshots, limit-change timestamps, treatment assignment/context, and post-intervention outcomes.
5. If no suitable public observational source exists, use a clearly labelled synthetic longitudinal environment to test causal estimators and diagnostics, while keeping synthetic evidence separate from empirical claims.

**No causal effect, ATE, CATE, propensity score, or model-performance result is established by this document.**
