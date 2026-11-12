# Methodology and identification policy

## Estimand

The primary target is the average treatment effect (ATE) of a clearly defined credit-limit increase on a binary default outcome over a prespecified horizon. Conditional effects (CATE) are secondary and require stronger sample-size and validation discipline.

## Treatment and outcomes

The current configuration names `treatment_indicator`, `default_6m` and `default_12m`. These are schema placeholders, not verified operational definitions. Before analysis, document the treatment threshold, index date, outcome event definition, censoring, follow-up window and eligibility criteria.

## Identification assumptions

Any observational estimate must discuss:
1. Consistency and a well-defined intervention.
2. Conditional exchangeability given measured pre-treatment covariates.
3. Positivity/overlap for treatment assignment.
4. Correct temporal ordering and no adjustment for post-treatment variables.
5. Interference assumptions and the unit of analysis.

These assumptions are not proven by model fit or predictive accuracy.

## Planned estimators

Double Machine Learning and causal forests are planned, not implemented. Propensity-score and outcome nuisance models must be cross-fitted where appropriate. Report ATE/CATE uncertainty, overlap, propensity distributions, effective sample size and sensitivity limitations.

## Prohibited shortcuts

Do not call predictive feature importance a causal effect. Do not include post-treatment credit limit, default outcomes or variables downstream of treatment in the adjustment set. Do not turn synthetic demonstrations into empirical claims.
