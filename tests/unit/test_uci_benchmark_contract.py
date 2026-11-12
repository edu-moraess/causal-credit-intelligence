import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "configs" / "datasets" / "uci_credit_default_benchmark_v1.json"


def load_contract():
    with CONTRACT_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_uci_benchmark_contract_has_expected_identity_and_source():
    contract = load_contract()

    assert contract["contract_id"] == "uci_credit_default_benchmark_v1"
    assert contract["source"]["provider"] == "UCI Machine Learning Repository"
    assert contract["source"]["doi"] == "10.24432/C55S3H"
    assert contract["source"]["license"] == "CC BY 4.0"
    assert contract["source"]["archive_sha256"] == (
        "56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602"
    )


def test_uci_benchmark_schema_and_feature_partition():
    contract = load_contract()
    expected_columns = contract["data_expectations"]["column_names"]
    features = contract["task"]["features"]

    assert contract["data_expectations"]["rows"] == 30000
    assert contract["data_expectations"]["columns"] == 25
    assert len(expected_columns) == 25
    assert len(features) == 23
    assert "ID" not in features
    assert contract["identifier"]["column"] == "ID"
    assert contract["task"]["target"] == "default payment next month"
    assert set(contract["task"]["allowed_target_values"]) == {0, 1}
    assert set(features).isdisjoint({"ID", contract["task"]["target"]})


def test_uci_contract_preserves_semantic_and_temporal_uncertainty():
    contract = load_contract()

    assert contract["temporal_scope"]["status"] == "partially_documented"
    assert contract["temporal_scope"]["exact_observation_cutoff"] is None
    assert contract["semantic_policies"]["EDUCATION"][
        "undocumented_in_primary_uci_description"
    ] == [0, 5, 6]
    assert contract["semantic_policies"]["MARRIAGE"][
        "undocumented_in_primary_uci_description"
    ] == [0]
    assert contract["semantic_policies"]["repayment_status"][
        "undocumented_in_primary_uci_description"
    ] == [-2, 0]
    assert contract["semantic_policies"]["bill_amounts"][
        "automatic_clipping_or_winsorization"
    ] is False


def test_uci_benchmark_is_not_misrepresented_as_causal_data():
    contract = load_contract()

    assert contract["causal_scope"]["causal_estimand_defined"] is False
    assert contract["causal_scope"]["treatment_defined"] is False
    assert contract["causal_scope"][
        "supports_credit_limit_intervention_effect_estimation"
    ] is False
    assert contract["processing_policy"]["training_performed"] is False
