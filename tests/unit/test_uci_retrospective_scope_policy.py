import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "configs/research/uci_pd_retrospective_benchmark_scope_v1.json"


def test_retrospective_scope_requires_explicit_user_approval_before_training():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    assert policy["status"] == "proposed_pending_user_scope_approval"
    assert policy["training_gate"]["training_authorized"] is False
    assert policy["training_gate"]["requires_explicit_user_approval_of_retrospective_scope"] is True
    assert policy["training_gate"]["requires_preprocessing_protocol_review"] is True
    assert policy["training_gate"]["requires_test_set_sealing"] is True


def test_random_split_is_not_temporal_validation():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    assert policy["evaluation_design"]["split_strategy"] == "stratified_random_by_target"
    assert policy["evaluation_design"]["temporal_validation"] is False
    assert policy["evaluation_design"]["out_of_time_validation"] is False


def test_unresolved_features_do_not_become_certified_or_safe_by_policy():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    assert policy["feature_policy"]["operational_availability"] == "unresolved_for_all_23_predictors"
    assert policy["feature_policy"]["feature_leakage"] == "not_determined"
    assert policy["feature_policy"]["require_fit_on_training_partition_only"] is True


def test_causal_and_production_tracks_remain_blocked():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    assert policy["causal_track"]["enabled"] is False
    assert policy["causal_track"]["requires_separate_longitudinal_intervention_dataset"] is True
    assert policy["production"]["authorized"] is False


def test_policy_is_json_serializable_and_preserves_test_set_sealing():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert json.loads(json.dumps(policy)) == policy
    assert "use once for final retrospective evaluation" in policy["evaluation_design"]["test_set_policy"]
