# Causal Credit Intelligence (CCI)

**ArqTech Labs** · Research foundation · v0.1.0

CCI is a research platform for studying the causal effect of credit-limit interventions on subsequent credit outcomes. It is designed to distinguish predictive risk modelling from causal effect estimation.

> **Current status:** foundation recovery. No real dataset has been validated, no model has been trained, and no causal effect has been estimated.

## Research question

What is the effect of a defined increase in a customer's credit limit on the probability of default over a specified follow-up horizon, conditional on defensible identification assumptions?

A predictive probability of default (PD) is not a causal effect. Observational estimates require explicit treatment definition, pre-treatment covariates, temporal alignment, overlap, confounding analysis and sensitivity diagnostics.

## Project principles

- Audit data before feature engineering or model fitting.
- Keep post-treatment variables and outcomes out of adjustment covariates.
- Preserve data, configuration and methodology hashes for every reported experiment.
- Label assumptions, estimates and limitations separately.
- Do not interpret scenario simulations as policy recommendations without validation.

## Repository

- `src/cci/data`: contracts, ingestion and structural validation.
- `src/cci/features`: explicit covariate selection.
- `src/cci/models`: PD and causal estimator interfaces.
- `src/cci/evaluation`: metric and diagnostic contracts.
- `src/cci/simulation`: scenario interface.
- `src/cci/reporting`: experiment records and audit trail.
- `configs/`: declarative configuration.
- `tests/`: automated tests.

## Setup

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

Optional ML and causal libraries are intentionally not installed in the foundation phase.

## Data

Place an explicitly approved CSV or Parquet file in `data/raw/`. CCI does not download data automatically. Do not commit personal or confidential customer data.

## Current gate

The next milestone is a reproducible Data Engine audit: schema, types, missingness, duplicate keys, temporal consistency and leakage checks. Model training remains blocked until that audit and the research protocol are approved.
