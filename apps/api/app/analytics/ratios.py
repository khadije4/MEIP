"""Expenditure-side ratios and mining-composition ratios (Section 9).
All safe against missing years / division by zero."""

from __future__ import annotations

from app.analytics.contribution import safe_share


def trade_balance(exports: float | None, imports: float | None) -> float | None:
    if exports is None or imports is None:
        return None
    return exports - imports


def investment_rate(gfcf: float | None, gdp_expenditure: float | None) -> float | None:
    return safe_share(gfcf, gdp_expenditure)


def consumption_rate(final_consumption: float | None, gdp_expenditure: float | None) -> float | None:
    return safe_share(final_consumption, gdp_expenditure)


def export_ratio(exports: float | None, gdp_expenditure: float | None) -> float | None:
    return safe_share(exports, gdp_expenditure)


def import_ratio(imports: float | None, gdp_expenditure: float | None) -> float | None:
    return safe_share(imports, gdp_expenditure)


def trade_openness(
    exports: float | None, imports: float | None, gdp_expenditure: float | None
) -> float | None:
    if exports is None or imports is None or gdp_expenditure in (None, 0):
        return None
    return (exports + imports) / gdp_expenditure * 100


def extractive_dependence(
    extractive_activities: float | None, gdp_activity_market_prices: float | None
) -> float | None:
    return safe_share(extractive_activities, gdp_activity_market_prices)


def snim_share_of_metallic(snim_iron: float | None, metallic_mineral_extraction: float | None) -> float | None:
    return safe_share(snim_iron, metallic_mineral_extraction)


def gold_copper_share_of_metallic(gold_copper: float | None, metallic_mineral_extraction: float | None) -> float | None:
    return safe_share(gold_copper, metallic_mineral_extraction)


def oil_gas_share_of_extractive(oil_gas_extraction: float | None, extractive_activities: float | None) -> float | None:
    return safe_share(oil_gas_extraction, extractive_activities)
