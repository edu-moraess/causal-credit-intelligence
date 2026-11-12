# Data dictionary — draft contract

This dictionary is a draft based on `configs/data.yaml`. It is not a substitute for source-specific validation or a signed-off business definition.

| Field | Role | Temporal requirement | Notes |
|---|---|---|---|
| `customer_id` | Identifier | At observation | Pseudonymous stable key; never publish direct identifiers |
| `observation_date` | Index date | At/before treatment | Must be parsed and timezone policy documented |
| `treatment_indicator` | Treatment | At index date | Binary flag; operational threshold must be defined |
| `credit_limit_before` | Pre-treatment context | Before intervention | Verify exact measurement timestamp |
| `credit_limit_after` | Post-treatment field | After intervention | Excluded from adjustment covariates |
| `default_6m` | Outcome | Follow-up | Define delinquency threshold, censoring and event window |
| `default_12m` | Outcome | Follow-up | Define delinquency threshold, censoring and event window |

## Required additions before analysis

Document source, unit of analysis, eligibility, repeated observations, currency/scale, missing-value codes, treatment threshold, index date, outcome event definition, follow-up and censoring. Candidate confounders must be explicitly listed and justified as pre-treatment variables.
