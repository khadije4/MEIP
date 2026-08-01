import pytest

from app.analytics.identities import (
    check_activity_factor_cost_identity,
    check_activity_market_price_identity,
    check_expenditure_identity,
)
from app.analytics.ratios import (
    consumption_rate,
    export_ratio,
    extractive_dependence,
    import_ratio,
    investment_rate,
    trade_balance,
    trade_openness,
)


def test_trade_balance_and_missing():
    assert trade_balance(169986.60, 226907.10) == pytest.approx(-56920.50)
    assert trade_balance(None, 100.0) is None


def test_investment_and_consumption_rate_safe_division():
    assert investment_rate(100.0, 0.0) is None
    assert investment_rate(100.0, 1000.0) == pytest.approx(10.0)
    assert consumption_rate(500.0, 1000.0) == pytest.approx(50.0)


def test_export_import_ratio_and_openness():
    assert export_ratio(200.0, 1000.0) == pytest.approx(20.0)
    assert import_ratio(300.0, 1000.0) == pytest.approx(30.0)
    assert trade_openness(200.0, 300.0, 1000.0) == pytest.approx(50.0)
    assert trade_openness(200.0, 300.0, None) is None


def test_extractive_dependence():
    assert extractive_dependence(78257.70, 429701.30) == pytest.approx(18.213, abs=0.01)


def test_2024_activity_identities_match_exactly():
    factor_cost_check = check_activity_factor_cost_identity(
        2024, primary=83568.90, secondary=130730.50, tertiary=181529.80, gdp_factor_cost=395829.20
    )
    assert factor_cost_check.status == "match"
    assert factor_cost_check.difference == pytest.approx(0.0, abs=0.5)

    market_price_check = check_activity_market_price_identity(
        2024, gdp_factor_cost=395829.20, net_taxes_products=33872.10,
        gdp_activity_market_prices=429701.30,
    )
    assert market_price_check.status == "match"


def test_2024_expenditure_identity_matches_with_zero_net_acquisition():
    check = check_expenditure_identity(
        2024,
        final_consumption=292929.50,
        gross_fixed_capital_formation=109585.40,
        inventory_changes=84106.90,
        net_acquisition_valuables=0.0,
        exports=169986.60,
        imports=226907.10,
        gdp_expenditure=429701.30,
    )
    assert check.status == "match"
    assert check.difference == pytest.approx(0.0, abs=0.5)


def test_expenditure_identity_is_partial_when_net_acquisition_is_na():
    check = check_expenditure_identity(
        1998,
        final_consumption=35512.56,
        gross_fixed_capital_formation=10196.39,
        inventory_changes=-6456.95,
        net_acquisition_valuables=None,  # NA in the source
        exports=9369.05,
        imports=10316.20,
        gdp_expenditure=38304.84,
    )
    assert check.status == "partial"
    assert check.missing_components == ["net_acquisition_valuables"]
    # Never silently treated as zero for the purposes of claiming an exact match:
    assert check.within_tolerance is None


def test_identity_missing_core_component_is_unavailable():
    check = check_activity_factor_cost_identity(2024, primary=None, secondary=1.0, tertiary=1.0, gdp_factor_cost=2.0)
    assert check.status == "unavailable"
    assert "primary_sector" in check.missing_components
