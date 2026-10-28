from ingredient_matcher.evaluate import calibrate_threshold, metrics_at_threshold, predict_rows
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
