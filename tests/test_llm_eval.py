import pytest

from ingredient_matcher.llm_eval import classification_metrics, cost_summary


def test_llm_metrics_reward_match_and_abstention():
    result = classification_metrics(
        ["queijo", "tomate", "NO_MATCH"],
        ["queijo", "tomate", "NO_MATCH"],
    )
    assert result["f1"] == 1.0
    assert result["no_match_accuracy"] == 1.0


def test_cost_summary_reports_cost_per_thousand_items():
    result = cost_summary(
        input_tokens=1_000,
        output_tokens=100,
        item_count=100,
        input_usd_per_million=1.0,
        output_usd_per_million=10.0,
    )
    assert result["total_usd"] == pytest.approx(0.002)
    assert result["usd_per_1000_items"] == pytest.approx(0.02)
