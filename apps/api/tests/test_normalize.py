from app.ingestion.normalize import normalize_text


def test_normalize_strips_accents_and_lowercases():
    assert normalize_text("PIB aux prix du marché") == "pib aux prix du marche"


def test_normalize_collapses_whitespace():
    assert normalize_text("  Élevage   et  chasse ") == "elevage et chasse"


def test_normalize_handles_apostrophes_and_parentheses():
    assert normalize_text("Activités financières et d'assurance") == "activites financieres et dassurance"


def test_normalize_empty_and_none():
    assert normalize_text("") == ""
    assert normalize_text(None) == ""
