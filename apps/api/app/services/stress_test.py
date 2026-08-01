from __future__ import annotations

from statistics import mean

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.analytics.stress_test import (
    ShockInput, calculate_concentration, dependency_series,
    sector_growth_contribution, simulate_multi_sector_shock,
    simulate_single_sector_shock, trend_label, vulnerability_metrics,
)
from app.models.indicator import Indicator
from app.services.series import get_indicator_or_404, get_ok_series

SOURCE = "ANSADE/CN"
UNIT = "Millions de MRU"
DISCLAIMER_FR = ("Cette simulation mesure uniquement l’impact comptable direct. Elle ne mesure pas "
                 "automatiquement les effets indirects sur l’emploi, les exportations, la consommation, "
                 "les fournisseurs ou les autres secteurs.")
DISCLAIMER_AR = ("تقيس هذه المحاكاة الأثر المحاسبي المباشر فقط، ولا تقيس تلقائياً الآثار غير المباشرة "
                 "على التشغيل أو الصادرات أو الاستهلاك أو الموردين أو القطاعات الأخرى.")
CURRENT_PRICE_FR = "Les valeurs sont nominales, aux prix courants; il ne s’agit pas d’une mesure de croissance réelle."
CURRENT_PRICE_AR = "القيم اسمية وبالأسعار الجارية؛ ولا تمثل مقياساً للنمو الحقيقي."

RANKING_GROUPS = {
    "main_sectors": ["primary_sector", "secondary_sector", "tertiary_sector"],
    "primary_branches": ["agriculture_forestry", "livestock_hunting", "fishing"],
    "secondary_branches": ["extractive_activities", "manufacturing", "construction_public_works"],
    "extractive_branches": ["oil_gas_extraction", "metallic_mineral_extraction", "other_extractive_activities"],
    "tertiary_branches": ["transport_information_communication", "commerce", "other_services", "public_administration"],
}


def _error(status: int, code: str, en: str, fr: str, ar: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message_en": en, "message_fr": fr, "message_ar": ar})


def _canonical(indicator: Indicator) -> Indicator:
    return indicator.alias_of if indicator.is_alias and indicator.alias_of is not None else indicator


def _sector(db: Session, code: str) -> Indicator:
    indicator = _canonical(get_indicator_or_404(db, code))
    if indicator.source_side != "activity" or indicator.code.startswith("gdp_") or indicator.code == "net_taxes_products":
        raise _error(400, "invalid_sector", f"'{code}' is not an activity sector.", "L’indicateur n’est pas un secteur d’activité.", "المؤشر ليس قطاع نشاط.")
    return indicator


def _value(db: Session, code: str, year: int) -> float:
    series = get_ok_series(db, code)
    if year not in series:
        raise _error(400, "value_not_available", f"No valid value for '{code}' in {year}.", f"Valeur non disponible pour {year}.", f"القيمة غير متاحة لسنة {year}.")
    return series[year]


def _gdp(db: Session, year: int) -> float:
    return _value(db, "gdp_activity_market_prices", year)


def _ancestors(indicator: Indicator) -> set[int]:
    ids: set[int] = set()
    node = indicator.parent
    while node is not None:
        canonical = _canonical(node)
        ids.add(canonical.id)
        node = node.parent
    return ids


def validate_compatible(indicators: list[Indicator]) -> None:
    conflicts: list[list[str]] = []
    for index, left in enumerate(indicators):
        for right in indicators[index + 1:]:
            if left.id == right.id or left.id in _ancestors(right) or right.id in _ancestors(left):
                conflicts.append([left.code, right.code])
    if conflicts:
        raise _error(400, "hierarchy_conflict", f"Parent/child or alias conflict: {conflicts}", f"Conflit hiérarchique parent/enfant ou alias : {conflicts}", f"تعارض هرمي بين الأصل والفرع أو الاسم البديل: {conflicts}")


def single(db: Session, year: int, indicator_code: str, shock_rate: float) -> dict:
    indicator = _sector(db, indicator_code)
    gdp = _gdp(db, year)
    result = simulate_single_sector_shock(year, indicator.code, shock_rate, sector_value=_value(db, indicator.code, year), baseline_activity_gdp=gdp)
    return {**result, "baseline_activity_gdp": gdp, "name_fr": indicator.name_fr, "name_ar": indicator.name_ar,
            "current_price_warning_fr": CURRENT_PRICE_FR, "current_price_warning_ar": CURRENT_PRICE_AR,
            "source": SOURCE, "unit": UNIT, "methodology_disclaimer_fr": DISCLAIMER_FR, "methodology_disclaimer_ar": DISCLAIMER_AR}


def multiple(db: Session, year: int, shocks: list[dict]) -> dict:
    indicators = [_sector(db, item["indicator_code"]) for item in shocks]
    validate_compatible(indicators)
    gdp = _gdp(db, year)
    inputs = [ShockInput(ind.code, _value(db, ind.code, year), item["shock_rate"]) for ind, item in zip(indicators, shocks)]
    result = simulate_multi_sector_shock(year, inputs, baseline_activity_gdp=gdp)
    names = {ind.code: ind for ind in indicators}
    effects = [{**effect, "name_fr": names[effect["indicator_code"]].name_fr, "name_ar": names[effect["indicator_code"]].name_ar} for effect in result["individual_effects"]]
    return {**result, "individual_effects": effects, "hierarchy_validation": "valid",
            "warnings_fr": [CURRENT_PRICE_FR, DISCLAIMER_FR], "warnings_ar": [CURRENT_PRICE_AR, DISCLAIMER_AR],
            "source": SOURCE, "unit": UNIT, "methodology_disclaimer_fr": DISCLAIMER_FR, "methodology_disclaimer_ar": DISCLAIMER_AR}


def ranking(db: Session, year: int, group: str) -> dict:
    if group not in RANKING_GROUPS:
        raise _error(400, "invalid_ranking_group", "Unsupported ranking group.", "Groupe de classement non pris en charge.", "مجموعة التصنيف غير مدعومة.")
    gdp_series = get_ok_series(db, "gdp_activity_market_prices")
    if year not in gdp_series:
        _gdp(db, year)
    items = []
    for code in RANKING_GROUPS[group]:
        indicator = _sector(db, code)
        series = get_ok_series(db, code)
        if year not in series:
            continue
        items.append({"indicator_code": code, "name_fr": indicator.name_fr, "name_ar": indicator.name_ar, **vulnerability_metrics(series, gdp_series, year)})
    items.sort(key=lambda item: item["shutdown_impact_pct"], reverse=True)
    for rank, item in enumerate(items, 1): item["vulnerability_rank"] = rank
    return {"year": year, "ranking_group": group, "sectors": items, "source": SOURCE, "unit": UNIT,
            "warning_fr": "Classement comptable expérimental; il ne mesure pas tous les effets économiques.",
            "warning_ar": "تصنيف محاسبي تجريبي؛ لا يقيس جميع الآثار الاقتصادية."}


def history(db: Session, code: str, start_year: int | None, end_year: int | None) -> dict:
    indicator = _sector(db, code)
    sector_series, gdp_series = get_ok_series(db, indicator.code), get_ok_series(db, "gdp_activity_market_prices")
    available = sorted(set(sector_series) | set(gdp_series))
    if not available: raise _error(400, "series_not_available", "Series unavailable.", "Série non disponible.", "السلسلة غير متاحة.")
    start, end = start_year or min(available), end_year or max(available)
    if start > end: raise _error(400, "invalid_period", "start_year must not exceed end_year.", "La première année doit précéder la dernière.", "يجب ألا تتجاوز سنة البداية سنة النهاية.")
    dependencies, missing = dependency_series(sector_series, gdp_series, start, end)
    contributions = sector_growth_contribution(sector_series, gdp_series)
    points = [{"year": y, "sector_value": sector_series[y], "activity_gdp": gdp_series[y], "dependency_pct": d, "nominal_growth_contribution_pct": contributions.get(y)} for y, d in sorted(dependencies.items())]
    min_year = min(dependencies, key=dependencies.get) if dependencies else None
    max_year = max(dependencies, key=dependencies.get) if dependencies else None
    return {"indicator_code": indicator.code, "name_fr": indicator.name_fr, "name_ar": indicator.name_ar,
            "start_year": start, "end_year": end, "points": points,
            "minimum_dependency_pct": dependencies.get(min_year), "minimum_year": min_year,
            "maximum_dependency_pct": dependencies.get(max_year), "maximum_year": max_year,
            "latest_dependency_pct": dependencies[max(dependencies)] if dependencies else None,
            "average_dependency_pct": mean(dependencies.values()) if dependencies else None, "trend": trend_label(dependencies),
            "missing_years": missing, "warnings_fr": ([f"Années manquantes : {missing}"] if missing else []),
            "warnings_ar": ([f"سنوات مفقودة: {missing}"] if missing else []), "source": SOURCE, "unit": UNIT}


def concentration(db: Session, year: int, group: str) -> dict:
    if group not in RANKING_GROUPS:
        raise _error(400, "invalid_ranking_group", "Unsupported concentration group.", "Groupe de concentration non pris en charge.", "مجموعة التركّز غير مدعومة.")
    indicators = [_sector(db, code) for code in RANKING_GROUPS[group]]
    validate_compatible(indicators)
    gdp = _gdp(db, year)
    values = {ind.code: _value(db, ind.code, year) for ind in indicators}
    result = calculate_concentration(values, gdp)
    included = [{"indicator_code": ind.code, "name_fr": ind.name_fr, "name_ar": ind.name_ar,
                 "economic_value": values[ind.code], "share_of_activity_gdp_pct": result["shares"][ind.code] * 100} for ind in indicators]
    return {"year": year, "ranking_group": group, "hhi": result["hhi"], "included_sectors": included,
            "interpretation": result["interpretation"], "source": SOURCE, "unit": UNIT,
            "methodology_warning_fr": "Mesure expérimentale de concentration comptable, et non mesure complète de résilience économique.",
            "methodology_warning_ar": "مقياس تجريبي للتركيز المحاسبي وليس مقياساً شاملاً للمرونة الاقتصادية."}

