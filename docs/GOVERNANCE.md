# Model and experiment governance

An experiment is reportable only when its data hash, configuration hash and methodology reference are recorded. Reports must also state sample definition, treatment/outcome definitions, estimator, uncertainty, diagnostics, software versions and limitations.

Raw data is not committed by default. Secrets, customer identifiers and confidential records must never enter public artifacts. Every data transformation must be reproducible and traceable.

Statuses such as planned, audited, fitted and completed must reflect evidence. A completed run is not automatically a valid causal study. Governance review is required before policy interpretation.
