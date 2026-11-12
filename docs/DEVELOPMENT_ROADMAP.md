# Development roadmap

## Foundation recovery
- [x] Reconcile imports and missing module interfaces (recovery implementation).
- [ ] Run the full test suite in a clean environment.
- [ ] Review the recovered implementation against original project intent.

## Phase 1 — Data Engine
- [ ] Define and approve the operational data dictionary.
- [ ] Audit a permitted dataset without modifying source data.
- [ ] Validate schema, types, missingness, duplicate keys and temporal order.
- [ ] Define pre-treatment covariates and leakage rules.
- [ ] Produce a signed-off data quality report and dataset fingerprint.

## Phase 2 — Predictive baseline
- [ ] Establish leakage-safe temporal splits.
- [ ] Fit and evaluate a PD baseline only after the data gate passes.
- [ ] Assess discrimination, calibration and stability.

## Phase 3 — Causal engine
- [ ] Document estimand and identification strategy.
- [ ] Diagnose overlap and confounding.
- [ ] Implement cross-fitted DML and causal forest.
- [ ] Report uncertainty and sensitivity analysis.

## Phase 4 — Governance and interface
- [ ] Reproducible experiment registry.
- [ ] Scenario interface gated by validated models.
- [ ] Reviewable dashboard and model cards.
