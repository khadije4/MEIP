"""Accounting-identity checks (Section 10). Each check compares a reported
aggregate against the sum of its components for a single year, with a small
rounding tolerance. When a component is unavailable (NA in the source), the
check is marked "partial" rather than silently assuming the missing
component is zero.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_TOLERANCE = 1.0  # Millions de MRU; source figures round to 2 decimals


@dataclass
class IdentityCheckResult:
    year: int
    label: str
    reported_value: float | None
    computed_value: float | None
    difference: float | None
    within_tolerance: bool | None
    status: str  # "match" | "mismatch" | "partial" | "unavailable"
    missing_components: list[str]


def check_activity_factor_cost_identity(
    year: int, primary: float | None, secondary: float | None, tertiary: float | None,
    gdp_factor_cost: float | None,
) -> IdentityCheckResult:
    missing = [
        name for name, v in (("primary_sector", primary), ("secondary_sector", secondary),
                              ("tertiary_sector", tertiary), ("gdp_factor_cost", gdp_factor_cost))
        if v is None
    ]
    if missing:
        return IdentityCheckResult(
            year, "primary + secondary + tertiary = GDP at factor cost",
            gdp_factor_cost, None, None, None, "unavailable", missing,
        )
    computed = primary + secondary + tertiary
    diff = gdp_factor_cost - computed
    return IdentityCheckResult(
        year, "primary + secondary + tertiary = GDP at factor cost",
        gdp_factor_cost, computed, diff, abs(diff) <= DEFAULT_TOLERANCE,
        "match" if abs(diff) <= DEFAULT_TOLERANCE else "mismatch", [],
    )


def check_activity_market_price_identity(
    year: int, gdp_factor_cost: float | None, net_taxes_products: float | None,
    gdp_activity_market_prices: float | None,
) -> IdentityCheckResult:
    missing = [
        name for name, v in (("gdp_factor_cost", gdp_factor_cost),
                              ("net_taxes_products", net_taxes_products),
                              ("gdp_activity_market_prices", gdp_activity_market_prices))
        if v is None
    ]
    if missing:
        return IdentityCheckResult(
            year, "GDP at factor cost + net taxes on products = GDP at market prices",
            gdp_activity_market_prices, None, None, None, "unavailable", missing,
        )
    computed = gdp_factor_cost + net_taxes_products
    diff = gdp_activity_market_prices - computed
    return IdentityCheckResult(
        year, "GDP at factor cost + net taxes on products = GDP at market prices",
        gdp_activity_market_prices, computed, diff, abs(diff) <= DEFAULT_TOLERANCE,
        "match" if abs(diff) <= DEFAULT_TOLERANCE else "mismatch", [],
    )


def check_expenditure_identity(
    year: int,
    final_consumption: float | None,
    gross_fixed_capital_formation: float | None,
    inventory_changes: float | None,
    net_acquisition_valuables: float | None,
    exports: float | None,
    imports: float | None,
    gdp_expenditure: float | None,
) -> IdentityCheckResult:
    label = (
        "final consumption + GFCF + inventory changes + net acquisition of valuables "
        "+ exports - imports = GDP (expenditure)"
    )
    core_components = {
        "final_consumption": final_consumption,
        "gross_fixed_capital_formation": gross_fixed_capital_formation,
        "inventory_changes": inventory_changes,
        "exports": exports,
        "imports": imports,
        "gdp_expenditure": gdp_expenditure,
    }
    missing_core = [name for name, v in core_components.items() if v is None]
    if missing_core:
        return IdentityCheckResult(
            year, label, gdp_expenditure, None, None, None, "unavailable", missing_core,
        )

    partial = net_acquisition_valuables is None
    net_acq = net_acquisition_valuables or 0.0
    computed = (
        final_consumption + gross_fixed_capital_formation + inventory_changes
        + net_acq + exports - imports
    )
    diff = gdp_expenditure - computed

    if partial:
        # Computed with the missing component excluded — never assumed zero
        # for the purposes of claiming an exact match.
        status = "partial"
        within_tolerance = None
    else:
        within_tolerance = abs(diff) <= DEFAULT_TOLERANCE
        status = "match" if within_tolerance else "mismatch"

    return IdentityCheckResult(
        year, label, gdp_expenditure, computed, diff, within_tolerance, status,
        ["net_acquisition_valuables"] if partial else [],
    )
