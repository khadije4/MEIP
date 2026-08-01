import pytest

from app.ingestion.numeric import NotNumericError, parse_numeric


def test_parse_plain_integer():
    assert parse_numeric("3200") == 3200.0


def test_parse_dot_decimal():
    assert parse_numeric("320.5") == 320.5


def test_parse_french_comma_decimal():
    assert parse_numeric("320,5") == 320.5


def test_parse_thousands_with_space():
    assert parse_numeric("3 200") == 3200.0


def test_parse_negative():
    assert parse_numeric("-45.2") == -45.2


def test_nonnumeric_text_raises():
    with pytest.raises(NotNumericError):
        parse_numeric("abc")


def test_empty_raises():
    with pytest.raises(NotNumericError):
        parse_numeric("")


def test_ambiguous_format_raises():
    with pytest.raises(NotNumericError):
        parse_numeric("1.234,56")
