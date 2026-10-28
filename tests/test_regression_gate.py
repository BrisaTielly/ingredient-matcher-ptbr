from ingredient_matcher.regression import regression_failures


def metrics(f1, top1):
    return {"test": {"f1": f1, "retrieval_top1_accuracy": top1}}


def test_regression_gate_accepts_values_within_tolerance():
    failures = regression_failures(
        {"matcher": metrics(0.90, 0.93)},
        {"matcher": metrics(0.895, 0.925)},
        ["matcher"],
        {"f1": 0.01, "retrieval_top1_accuracy": 0.01},
    )
    assert failures == []


def test_regression_gate_rejects_material_f1_drop():
    failures = regression_failures(
        {"matcher": metrics(0.90, 0.93)},
        {"matcher": metrics(0.88, 0.93)},
        ["matcher"],
        {"f1": 0.01, "retrieval_top1_accuracy": 0.01},
    )
    assert failures == ["matcher f1 dropped 0.0200, above the 0.0100 limit"]
