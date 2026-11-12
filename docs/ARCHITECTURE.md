# Architecture

CCI separates data controls, predictive modelling, causal estimation, diagnostics, simulation and governance.

1. Data layer: explicit ingestion and versioned contract.
2. Validation: structural, missingness, duplicate, temporal and leakage checks.
3. Features: explicit pre-treatment covariate selection.
4. PD layer: predictive baseline, separate from causal estimands.
5. Causal layer: planned DML and causal forest interfaces.
6. Evaluation: predictive metrics and causal diagnostics kept distinct.
7. Simulation: disabled until a validated causal estimator exists.
8. Reporting: hashes and audit trail.

The Streamlit interface is a presentation layer only; it must not bypass validation or invoke training implicitly.
