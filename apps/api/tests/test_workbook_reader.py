"""Tests against the real ANSADE/CN workbooks in data/raw, asserting the
exact published figures (see Section 18 of the spec / docs/DATA_DICTIONARY.md)."""

import pytest

from app.ingestion.datasets_config import DATASET_SPECS
from app.ingestion.workbook_reader import read_workbook

EXPENDITURE_SPEC = next(s for s in DATASET_SPECS if s.code == "gdp_by_expenditure")
ACTIVITY_SPEC = next(s for s in DATASET_SPECS if s.code == "gdp_by_activity")


def _value(result, code, year):
    row = next(r for r in result.rows if r.spec.code == code)
    cell = next(c for c in row.cells if c.year == year)
    return cell


@pytest.fixture(scope="module")
def expenditure_result(real_data_raw_dir):
    path = real_data_raw_dir / EXPENDITURE_SPEC.filename
    if not path.exists():
        pytest.skip(f"Real data file not present: {path}")
    return read_workbook(path, EXPENDITURE_SPEC.sheet_name, EXPENDITURE_SPEC.row_specs)


@pytest.fixture(scope="module")
def activity_result(real_data_raw_dir):
    path = real_data_raw_dir / ACTIVITY_SPEC.filename
    if not path.exists():
        pytest.skip(f"Real data file not present: {path}")
    return read_workbook(path, ACTIVITY_SPEC.sheet_name, ACTIVITY_SPEC.row_specs)


def test_year_range(expenditure_result, activity_result):
    assert expenditure_result.start_year == 1998
    assert expenditure_result.end_year == 2024
    assert activity_result.start_year == 1998
    assert activity_result.end_year == 2024


def test_all_rows_consumed(expenditure_result, activity_result):
    assert len(expenditure_result.rows) == len(EXPENDITURE_SPEC.row_specs) == 12
    assert len(activity_result.rows) == len(ACTIVITY_SPEC.row_specs) == 27


def test_no_label_mismatches(expenditure_result, activity_result):
    assert expenditure_result.warnings == []
    assert activity_result.warnings == []


def test_2024_activity_values_exact(activity_result):
    assert _value(activity_result, "primary_sector", 2024).value == pytest.approx(83568.90)
    assert _value(activity_result, "secondary_sector", 2024).value == pytest.approx(130730.50)
    assert _value(activity_result, "tertiary_sector", 2024).value == pytest.approx(181529.80)
    assert _value(activity_result, "gdp_factor_cost", 2024).value == pytest.approx(395829.20)
    assert _value(activity_result, "net_taxes_products", 2024).value == pytest.approx(33872.10)
    assert _value(activity_result, "gdp_activity_market_prices", 2024).value == pytest.approx(429701.30)


def test_2024_expenditure_values_exact(expenditure_result):
    assert _value(expenditure_result, "gdp_expenditure", 2024).value == pytest.approx(429701.30)
    assert _value(expenditure_result, "exports", 2024).value == pytest.approx(169986.60)
    assert _value(expenditure_result, "imports", 2024).value == pytest.approx(226907.10)


def test_2018_gdp_reconciliation_values(expenditure_result, activity_result):
    expenditure_gdp = _value(expenditure_result, "gdp_expenditure", 2018).value
    activity_gdp = _value(activity_result, "gdp_activity_market_prices", 2018).value
    assert expenditure_gdp == pytest.approx(262320.02)
    assert activity_gdp == pytest.approx(266637.60)
    assert abs(activity_gdp - expenditure_gdp) == pytest.approx(4317.58, abs=0.01)


def test_primary_sector_alias_matches_agriculture_fishing_forestry(activity_result):
    for year in (1998, 2010, 2024):
        primary = _value(activity_result, "primary_sector", year).value
        alias = _value(activity_result, "agriculture_fishing_forestry", year).value
        assert primary == pytest.approx(alias)


def test_agriculture_subsectors_sum_to_parent(activity_result):
    for year in (2015, 2024):
        parent = _value(activity_result, "agriculture_fishing_forestry", year).value
        children_sum = (
            _value(activity_result, "agriculture_forestry", year).value
            + _value(activity_result, "livestock_hunting", year).value
            + _value(activity_result, "fishing", year).value
        )
        assert children_sum == pytest.approx(parent, abs=0.05)


def test_metallic_mineral_extraction_equals_snim_plus_gold_copper(activity_result):
    for year in (2020, 2024):
        parent = _value(activity_result, "metallic_mineral_extraction", year).value
        children_sum = (
            _value(activity_result, "snim_iron", year).value
            + _value(activity_result, "gold_copper", year).value
        )
        assert children_sum == pytest.approx(parent, abs=0.05)


def test_sectors_sum_to_gdp_factor_cost(activity_result):
    for year in (2024,):
        total = (
            _value(activity_result, "primary_sector", year).value
            + _value(activity_result, "secondary_sector", year).value
            + _value(activity_result, "tertiary_sector", year).value
        )
        assert total == pytest.approx(_value(activity_result, "gdp_factor_cost", year).value, abs=0.05)


def test_net_acquisition_valuables_na_is_missing_not_zero(expenditure_result):
    cell_1998 = _value(expenditure_result, "net_acquisition_valuables", 1998)
    assert cell_1998.is_missing is True
    assert cell_1998.value is None
    assert cell_1998.quality_flag == "missing"

    cell_2019 = _value(expenditure_result, "net_acquisition_valuables", 2019)
    assert cell_2019.is_missing is False
    assert cell_2019.value == pytest.approx(1480.00)

    cell_2024 = _value(expenditure_result, "net_acquisition_valuables", 2024)
    assert cell_2024.is_missing is False
    assert cell_2024.value == pytest.approx(0.00)
