from ingredient_matcher.data import generate_rows, read_canonicals


def test_dataset_is_deterministic_and_has_expected_size():
    canonicals = read_canonicals()
    first = generate_rows(canonicals)
    second = generate_rows(canonicals)
    assert first == second
    assert len(canonicals) == 100
    assert len(first) == 330


def test_source_groups_do_not_cross_splits():
    rows = generate_rows(read_canonicals())
    seen: dict[str, str] = {}
    for row in rows:
        previous = seen.setdefault(row["source_group"], row["split"])
        assert previous == row["split"]


def test_test_set_is_reviewable_size_and_contains_no_match():
    rows = generate_rows(read_canonicals())
    test = [row for row in rows if row["split"] == "test"]
    assert 60 <= len(test) <= 80
    assert sum(row["canonical_id"] == "NO_MATCH" for row in test) == 6
