from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.analytics.growth import summarize
from app.analytics.forecasting import generate_forecast
from app.analytics.ratios import investment_rate, trade_balance
from app.models.dataset import Dataset
from app.schemas.assistant import AssistantAnswer, EvidenceValue
from app.services.series import get_indicator_or_404, get_ok_series
from app.services import recommendations


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower().replace("’", "'"))
    return "".join(c for c in text if not unicodedata.combining(c))


def _language(question: str, requested: str | None) -> str:
    if requested in {"ar", "fr"}:
        return requested
    return "ar" if re.search(r"[\u0600-\u06ff]", question) else "fr"


ALIASES = {
    "secondary_sector": ["secteur secondaire", "القطاع الثانوي"],
    "fishing": ["peche", "الصيد"],
    "extractive_activities": ["activites extractives", "extractives", "الاستخراج", "الاستخراجية"],
    "gold_copper": ["or et le cuivre", "or et cuivre", "الذهب والنحاس"],
    "gdp_activity_market_prices": ["pib", "الناتج المحلي", "الناتج"],
}


def _evidence(db: Session, code: str, year: int, value: float, language: str) -> EvidenceValue:
    ind = get_indicator_or_404(db, code)
    dataset = db.query(Dataset).filter(Dataset.code == ("gdp_by_activity" if ind.source_side == "activity" else "gdp_by_expenditure")).first()
    return EvidenceValue(indicator_code=code, indicator_name=(ind.name_ar if language == "ar" else ind.name_fr) or ind.name_fr,
        year=year, value=value, source_side=ind.source_side, source_file=dataset.original_filename if dataset else "",
        worksheet=dataset.worksheet_name if dataset else "", unit=ind.unit)


def answer_question(db: Session, question: str, requested_language: str | None = None) -> AssistantAnswer:
    language = _language(question, requested_language)
    q = _norm(question)
    years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", q)]
    year = years[0] if years else 2024

    def response(intent: str, answer_fr: str, answer_ar: str, evidence: list[EvidenceValue], calculation: str, warnings: list[str] | None = None):
        return AssistantAnswer(language=language, intent=intent, answer=answer_ar if language == "ar" else answer_fr,
            values_used=evidence, calculation=calculation, warnings=warnings or [])

    if ("secteur secondaire" in q or "القطاع الثانوي" in q) and any(term in q for term in ("arrete", "arrêt", "faire", "توقف", "نفعل")):
        plan = recommendations.generate(db, year, [{"indicator_code": "secondary_sector", "shock_rate": 1.0}], "one_year")
        stress = plan["stress_test"]
        evidence = [_evidence(db, "secondary_sector", year, stress["individual_effects"][0]["sector_value"], language),
                    _evidence(db, "gdp_activity_market_prices", year, stress["baseline_activity_gdp"], language)]
        answer_fr = (f"Scénario : arrêt complet du secteur secondaire en {year}. Impact comptable calculé : "
            f"{stress['total_direct_gdp_impact_pct']:.2f} % du PIB d’activité. Les vulnérabilités principales concernent la continuité des infrastructures, les intrants et la concentration productive. "
            "Les options de réponse sont organisées en quatre horizons distincts ci-dessous. À suivre : production secondaire et PIB par activité. "
            "Limites : les données nationales observées ne comprennent pas l’emploi, les entreprises ni le coût budgétaire; les impacts sont calculés et les actions sont fondées sur des règles.")
        answer_ar = (f"السيناريو: توقف كامل للقطاع الثانوي سنة {year}. الأثر المحاسبي المحسوب: "
            f"{stress['total_direct_gdp_impact_pct']:.2f}٪ من ناتج الأنشطة. ترتبط مواطن الهشاشة باستمرارية البنية التحتية والمدخلات والتركيز الإنتاجي. "
            "تُنظم خيارات الاستجابة ضمن أربعة آفاق مختلفة أدناه. المتابعة: إنتاج القطاع الثانوي والناتج حسب الأنشطة. "
            "الحدود: لا تتضمن البيانات الوطنية المرصودة التشغيل أو بيانات المؤسسات أو التكلفة المالية؛ الأثر محسوب والخيارات قائمة على قواعد.")
        return AssistantAnswer(language=language, intent="secondary_sector_response", answer=answer_ar if language == "ar" else answer_fr,
            values_used=evidence, calculation="direct_loss = secondary_sector × 100%; impact = direct_loss / GDP × 100",
            warnings=[recommendations.DISCLAIMER_AR if language == "ar" else recommendations.DISCLAIMER_FR], recommendation_plan=plan)

    if ("solde commercial" in q or "الميزان التجاري" in q):
        ex, im = get_ok_series(db, "exports"), get_ok_series(db, "imports")
        value = trade_balance(ex.get(year), im.get(year))
        if value is None:
            return response("trade_balance", "Donnée indisponible.", "البيانات غير متاحة.", [], "exports - imports", ["Required value is missing."])
        ev = [_evidence(db, "exports", year, ex[year], language), _evidence(db, "imports", year, im[year], language)]
        return response("trade_balance", f"Le solde commercial en {year} était de {value:,.2f} millions de MRU.", f"بلغ الميزان التجاري سنة {year} مقدار {value:,.2f} مليون أوقية جديدة.", ev, "exports - imports")

    if ("taux d'investissement" in q or "taux d’investissement" in q or "معدل الاستثمار" in q):
        gfcf, gdp = get_ok_series(db, "gross_fixed_capital_formation"), get_ok_series(db, "gdp_expenditure")
        value = investment_rate(gfcf.get(year), gdp.get(year))
        if value is None:
            return response("investment_rate", "Donnée indisponible.", "البيانات غير متاحة.", [], "GFCF / GDP expenditure × 100", ["Required value is missing."])
        ev = [_evidence(db, "gross_fixed_capital_formation", year, gfcf[year], language), _evidence(db, "gdp_expenditure", year, gdp[year], language)]
        return response("investment_rate", f"Le taux d'investissement en {year} était de {value:.2f} %.", f"بلغ معدل الاستثمار سنة {year} نسبة {value:.2f}٪.", ev, "gross_fixed_capital_formation / gdp_expenditure × 100")

    if ("difference" in q and "pib" in q) or ("الفرق" in q and "الناتج" in q):
        act, exp = get_ok_series(db, "gdp_activity_market_prices"), get_ok_series(db, "gdp_expenditure")
        common = sorted(set(act) & set(exp)); chosen = year if years else common[-1]
        diff = act[chosen] - exp[chosen]
        ev = [_evidence(db, "gdp_activity_market_prices", chosen, act[chosen], language), _evidence(db, "gdp_expenditure", chosen, exp[chosen], language)]
        return response("gdp_reconciliation", f"En {chosen}, l'écart activité moins dépense était de {diff:,.2f} millions de MRU.", f"في سنة {chosen} بلغ الفرق بين ناتج الأنشطة وناتج الإنفاق {diff:,.2f} مليون أوقية جديدة.", ev, "gdp_activity_market_prices - gdp_expenditure")

    if ("plus grand secteur" in q or "اكبر قطاع" in q):
        values = {c: get_ok_series(db, c).get(year) for c in ("primary_sector", "secondary_sector", "tertiary_sector")}
        valid = {c: v for c, v in values.items() if v is not None}
        if not valid: return response("largest_sector", "Donnée indisponible.", "البيانات غير متاحة.", [], "max(main sectors)")
        code = max(valid, key=valid.get); ev = [_evidence(db, code, year, valid[code], language)]
        return response("largest_sector", f"En {year}, le plus grand secteur était {ev[0].indicator_name}, avec {valid[code]:,.2f} millions de MRU.", f"في سنة {year} كان أكبر قطاع هو {ev[0].indicator_name} بقيمة {valid[code]:,.2f} مليون أوقية جديدة.", ev, "maximum among primary, secondary and tertiary sectors")

    if ("compare" in q or "قارن" in q) and (("peche" in q and "extract" in q) or ("الصيد" in q and "الاستخراج" in q)):
        fishing, extractive = get_ok_series(db, "fishing"), get_ok_series(db, "extractive_activities")
        y = year if years else max(set(fishing) & set(extractive))
        ev = [_evidence(db, "fishing", y, fishing[y], language), _evidence(db, "extractive_activities", y, extractive[y], language)]
        return response("compare", f"En {y}, la pêche valait {fishing[y]:,.2f} et les activités extractives {extractive[y]:,.2f} millions de MRU.", f"في سنة {y} بلغت قيمة الصيد {fishing[y]:,.2f} والأنشطة الاستخراجية {extractive[y]:,.2f} مليون أوقية جديدة.", ev, "direct comparison of imported observations")

    if "plus volatile" in q or "الاكثر تقلب" in q:
        codes = ("fishing", "extractive_activities", "manufacturing", "construction_public_works", "commerce", "transport")
        ranked = sorted(((c, summarize(get_ok_series(db, c)).volatility) for c in codes), key=lambda item: item[1] if item[1] is not None else -1, reverse=True)
        top = ranked[:3]; latest = max(get_ok_series(db, top[0][0])); ev = [_evidence(db, c, latest, get_ok_series(db, c)[latest], language) for c,_ in top]
        labels = ", ".join(f"{e.indicator_name} ({v:.2f} %)" for e,(_,v) in zip(ev,top))
        return response("volatility_ranking", f"Les branches les plus volatiles sont : {labels}.", f"الفروع الأكثر تقلبا هي: {labels}.", ev, "sample standard deviation of valid consecutive nominal annual growth")

    if "prevision" in q or "توقع" in q:
        series = get_ok_series(db, "gdp_activity_market_prices"); fc = generate_forecast(series)
        latest = max(series); ev = [_evidence(db, "gdp_activity_market_prices", latest, series[latest], language)]
        values = ", ".join(f"{y}: {v:,.2f}" for y,v in zip(fc.horizon_years, fc.predicted_values))
        warning = "Experimental estimate; not an official ANSADE forecast."
        return response("forecast", f"Prévision expérimentale du PIB ({fc.model_name}, fiabilité {fc.reliability}) : {values}. Elle n'est pas officielle.", f"التوقع التجريبي للناتج ({fc.model_name}، الموثوقية {fc.reliability}): {values}. وهو غير رسمي.", ev, "chronological backtesting against naive last-value baseline", [warning])

    matched = next((code for code, aliases in ALIASES.items() if any(alias in q for alias in aliases)), None)
    if matched:
        series = get_ok_series(db, matched)
        if ("plus baisse" in q or "اكبر انخفاض" in q):
            s = summarize(series)
            y = s.largest_decrease_year
            ev = [_evidence(db, matched, y, series[y], language)] if y else []
            return response("largest_decrease", f"La plus forte baisse nominale a eu lieu en {y} ({s.largest_decrease_pct:.2f} %).", f"حدث أكبر انخفاض اسمي سنة {y} بنسبة {s.largest_decrease_pct:.2f}٪.", ev, "minimum valid consecutive annual growth")
        if "evolu" in q or "تطور" in q:
            s = summarize(series); ev = [_evidence(db, matched, s.latest_year, s.latest_value, language)]
            if s.total_pct_change is None:
                return response("evolution", f"Entre {min(series)} et {max(series)}, {ev[0].indicator_name} est passé de {series[min(series)]:,.2f} à {series[max(series)]:,.2f} millions de MRU. Le pourcentage total est indisponible car la première valeur est nulle.", f"بين {min(series)} و{max(series)} انتقل {ev[0].indicator_name} من {series[min(series)]:,.2f} إلى {series[max(series)]:,.2f} مليون أوقية جديدة. النسبة الكلية غير متاحة لأن القيمة الأولى صفر.", ev, "endpoint comparison; percentage unavailable when first value is zero", ["Total percentage change is unavailable because the first value is zero."])
            return response("evolution", f"Entre {min(series)} et {max(series)}, {ev[0].indicator_name} est passé de {series[min(series)]:,.2f} à {series[max(series)]:,.2f} millions de MRU, soit {s.total_pct_change:.2f} % en valeur nominale.", f"بين {min(series)} و{max(series)} انتقل {ev[0].indicator_name} من {series[min(series)]:,.2f} إلى {series[max(series)]:,.2f} مليون أوقية جديدة، أي {s.total_pct_change:.2f}٪ اسميا.", ev, "(last - first) / abs(first) × 100")
        if year in series:
            ev = [_evidence(db, matched, year, series[year], language)]
            side = "activité" if ev[0].source_side == "activity" else "dépense"
            return response("indicator_value", f"{ev[0].indicator_name} en {year}: {series[year]:,.2f} millions de MRU (table {side}).", f"بلغ {ev[0].indicator_name} سنة {year} مقدار {series[year]:,.2f} مليون أوقية جديدة.", ev, "direct imported observation")

    return AssistantAnswer(language=language, intent="unsupported", answer="Je ne peux répondre qu'aux questions couvertes par les comptes nationaux importés." if language == "fr" else "لا يمكنني الإجابة إلا عن الأسئلة التي تغطيها بيانات الحسابات الوطنية المستوردة.", values_used=[], calculation="none", warnings=["No supported deterministic intent matched."], supported=False)
