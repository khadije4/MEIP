"""Computes and persists the GDP reconciliation between the two independent
series: gdp_expenditure (table 4.9.1) and gdp_activity_market_prices
(table 4.9.2). They are never merged — this only records their divergence
per year so the frontend can show both values transparently.

percentage_difference is computed against gdp_activity_market_prices, since
that is the series used elsewhere for sector-contribution calculations
(see docs/DATA_DICTIONARY.md).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.economic_value import EconomicValue
from app.models.indicator import Indicator
from app.models.reconciliation import ReconciliationIssue

FIRST_CODE = "gdp_expenditure"
SECOND_CODE = "gdp_activity_market_prices"

_SEVERITY_THRESHOLDS = (
    (0.5, "green"),
    (2.0, "yellow"),
    (5.0, "orange"),
)


def _severity_for(pct_diff: float) -> str:
    for threshold, severity in _SEVERITY_THRESHOLDS:
        if pct_diff < threshold:
            return severity
    return "red"


def _explanations(year: int, first_value: float, second_value: float, abs_diff: float, pct_diff: float) -> tuple[str, str]:
    fr = (
        f"En {year}, le PIB par l'approche dépenses ({first_value:,.2f} MRU) et le PIB par "
        f"l'approche activité aux prix du marché ({second_value:,.2f} MRU) diffèrent de "
        f"{abs_diff:,.2f} MRU ({pct_diff:.2f} %). Les deux séries proviennent de l'ANSADE/CN "
        f"et ne sont pas fusionnées."
    )
    ar = (
        f"في سنة {year}، يختلف الناتج المحلي الإجمالي حسب الإنفاق ({first_value:,.2f} أوقية) "
        f"عن الناتج المحلي الإجمالي حسب النشاط بأسعار السوق ({second_value:,.2f} أوقية) "
        f"بفارق {abs_diff:,.2f} أوقية ({pct_diff:.2f}%). كلتا السلسلتين مصدرهما "
        f"ANSADE/CN ولا يتم دمجهما."
    )
    return fr, ar


def compute_gdp_reconciliation(db: Session) -> int:
    first = db.query(Indicator).filter(Indicator.code == FIRST_CODE).first()
    second = db.query(Indicator).filter(Indicator.code == SECOND_CODE).first()
    if first is None or second is None:
        return 0

    # Idempotent: recompute from scratch for this indicator pair.
    db.query(ReconciliationIssue).filter(
        ReconciliationIssue.first_indicator_id == first.id,
        ReconciliationIssue.second_indicator_id == second.id,
    ).delete()

    first_values = {
        v.year: v.value
        for v in db.query(EconomicValue).filter(
            EconomicValue.indicator_id == first.id, EconomicValue.value.isnot(None)
        )
    }
    second_values = {
        v.year: v.value
        for v in db.query(EconomicValue).filter(
            EconomicValue.indicator_id == second.id, EconomicValue.value.isnot(None)
        )
    }

    created = 0
    for year in sorted(set(first_values) & set(second_values)):
        v1, v2 = first_values[year], second_values[year]
        abs_diff = abs(v1 - v2)
        pct_diff = (abs_diff / abs(v2) * 100) if v2 != 0 else 0.0
        severity = _severity_for(pct_diff)
        explanation_fr, explanation_ar = _explanations(year, v1, v2, abs_diff, pct_diff)

        db.add(
            ReconciliationIssue(
                year=year,
                first_indicator_id=first.id,
                second_indicator_id=second.id,
                first_value=v1,
                second_value=v2,
                absolute_difference=abs_diff,
                percentage_difference=pct_diff,
                severity=severity,
                explanation_fr=explanation_fr,
                explanation_ar=explanation_ar,
            )
        )
        created += 1

    db.commit()
    return created
