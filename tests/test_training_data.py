from ingredient_matcher.train import training_pairs


def test_training_pairs_exclude_no_match_and_holdout_splits(tmp_path):
    dataset = tmp_path / "dataset.csv"
    dataset.write_text(
        "raw_name,canonical_id,canonical_name,split\n"
        "QJ MUSS,queijo_mussarela,Queijo mussarela,train\n"
        "DETERGENTE,NO_MATCH,Sem correspondência,train\n"
        "TOMATE,tomate,Tomate italiano,test\n",
        encoding="utf-8",
    )
    assert training_pairs(dataset) == [("query: queijo mussarela", "passage: queijo mussarela")]
