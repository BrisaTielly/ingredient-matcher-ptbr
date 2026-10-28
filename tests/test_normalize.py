from ingredient_matcher.normalize import normalize


def test_normalize_removes_units_accents_and_expands_abbreviations():
    assert normalize("QJ MUSS FAT. 1KG") == "queijo mussarela fatiado"


def test_normalize_collapses_noise():
    assert normalize("  AÇÚCAR---CRISTAL, PCT 500G ") == "acucar cristal"
