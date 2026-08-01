from app.ingestion.label_clean import clean_label


def test_strips_nbsp_indentation():
    assert clean_label("\xa0\xa0\xa0\xa0Secteur primaire") == "Secteur primaire"


def test_strips_simple_numbering():
    assert clean_label("\xa0\xa0\xa02. Activités extractives") == "Activités extractives"


def test_strips_two_level_numbering_with_space():
    assert clean_label("\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa01. 1 Agriculture, Sylviculture et Exploit. Forestière") == \
        "Agriculture, Sylviculture et Exploit. Forestière"


def test_strips_dotted_numbering():
    assert clean_label("\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa02.2. Industries extractives autre que produits petroliers et gaziers") == \
        "Industries extractives autre que produits petroliers et gaziers"


def test_strips_three_level_numbering():
    assert clean_label("\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa02. 2.1 Extraction des minerais métaliques") == \
        "Extraction des minerais métaliques"


def test_no_numbering_left_untouched():
    assert clean_label("\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0Fer_SNIM") == "Fer_SNIM"


def test_no_indentation_flat_label():
    assert clean_label("Importation") == "Importation"


def test_none_returns_empty():
    assert clean_label(None) == ""
