from ingredient_matcher.evaluate import (
    bootstrap_intervals,
    calibrate_threshold,
    metrics_at_threshold,
    predict_rows,
)
from ingredient_matcher.matchers import Candidate


class StubMatcher:
    def search(self, raw_name, top_k=5):
        if raw_name == "known":
            return [Candidate("known_id", "Known", 0.9), Candidate("other", "Other", 0.1)]
        return [Candidate("other", "Other", 0.2), Candidate("known_id", "Known", 0.1)]


def rows():
    return [
        {"raw_name": "known", "canonical_id": "known_id"},
        {"raw_name": "unknown", "canonical_id": "NO_MATCH"},
    ]


def test_metrics_reward_correct_match_and_correct_abstention():
    predictions = predict_rows(StubMatcher(), rows())
    metrics = metrics_at_threshold(predictions, 0.5)
    assert metrics["accuracy"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["no_match_accuracy"] == 1.0


def test_calibration_uses_scores_to_find_separating_threshold():
    predictions = predict_rows(StubMatcher(), rows())
    threshold, metrics = calibrate_threshold(predictions)
    assert 0.2 < threshold <= 0.9
    assert metrics["accuracy"] == 1.0


def test_bootstrap_intervals_are_deterministic_and_bounded():
    predictions = predict_rows(StubMatcher(), rows())
    first = bootstrap_intervals(predictions, 0.5, iterations=100, seed=7)
    second = bootstrap_intervals(predictions, 0.5, iterations=100, seed=7)
    assert first == second
    assert first["f1"] == {"low": 1.0, "high": 1.0}
    assert first["no_match_accuracy"] == {"low": 1.0, "high": 1.0}
