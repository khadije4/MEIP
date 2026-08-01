from __future__ import annotations

from statistics import mean, pstdev

from sqlalchemy.orm import Session

from app.analytics.recommendations import alternative_score, classify_risk, confidence_from_completeness
from app.analytics.stress_test import growth_rates
from app.services import stress_test
from app.services.series import get_indicator_or_404, get_ok_series

DISCLAIMER_FR = "Options de réponse fondées sur les comptes nationaux disponibles; elles ne remplacent pas une étude sectorielle, budgétaire, sociale ou environnementale."
DISCLAIMER_AR = "خيارات استجابة مبنية على الحسابات الوطنية المتاحة، ولا تعوض دراسة قطاعية أو مالية أو اجتماعية أو بيئية."
THRESHOLDS_FR = "Les seuils de risque sont expérimentaux et ne constituent pas des normes officielles."
THRESHOLDS_AR = "عتبات المخاطر تجريبية ولا تمثل معايير حكومية رسمية."
LIMIT_FR = "À valider par des études complémentaires; aucun coût, emploi ou effet au niveau des entreprises n’est estimé."
LIMIT_AR = "يتطلب التحقق بدراسات إضافية؛ لا يتم تقدير التكلفة أو التشغيل أو الأثر على مستوى المؤسسات."

SECONDARY_CODES = {"secondary_sector", "extractive_activities", "manufacturing", "water_electricity", "construction_public_works", "metallic_mineral_extraction", "snim_iron", "gold_copper", "oil_gas_extraction"}
KNOWN_SECTORS = SECONDARY_CODES | {"primary_sector", "agriculture_forestry", "livestock_hunting", "fishing", "tertiary_sector", "commerce", "transport", "information_communication", "other_services", "public_administration"}
SECTOR_ACTIONS = {code: code for code in KNOWN_SECTORS}  # public catalogue compatibility

MONITORING = {
    "secondary_sector": ["secondary_sector", "gdp_activity_market_prices"],
    "extractive_activities": ["extractive_activities", "exports", "gdp_activity_market_prices"],
    "fishing": ["fishing", "exports", "gdp_activity_market_prices"],
    "commerce": ["commerce", "imports", "final_consumption"],
    "construction_public_works": ["construction_public_works", "gross_fixed_capital_formation"],
    "transport": ["transport", "imports", "exports"],
}

# Each stable action code belongs to exactly one horizon.
HORIZON_ACTIONS = {
    "immediate": ("Maintenir les opérations et infrastructures essentielles", "الحفاظ على العمليات والبنية التحتية الأساسية", "Préserver l’électricité, l’eau, le transport, le port, le rail et les télécommunications nécessaires à la production essentielle.", "حماية الكهرباء والمياه والنقل والميناء والسكك الحديدية والاتصالات اللازمة للإنتاج الأساسي.", "Maintenir les fonctions productives essentielles pendant la crise.", "الحفاظ على الوظائف الإنتاجية الأساسية أثناء الأزمة.", "critical"),
    "stabilization": ("Rétablir les intrants et la liquidité des entreprises viables", "استعادة المدخلات والسيولة للمؤسسات القابلة للاستمرار", "Fournir un appui temporaire et conditionnel et rétablir l’accès aux intrants, pièces détachées et fournisseurs locaux.", "تقديم دعم مؤقت ومشروط واستعادة الوصول إلى المدخلات وقطع الغيار والموردين المحليين.", "Réduire les blocages vérifiés et stabiliser les chaînes d’approvisionnement.", "تقليص الاختناقات المثبتة واستقرار سلاسل الإمداد.", "high"),
    "recovery": ("Moderniser et reconstruire la capacité productive", "تحديث وإعادة بناء القدرة الإنتاجية", "Soutenir la modernisation des équipements, les services des zones industrielles, le financement des PME et la transformation locale.", "دعم تحديث المعدات وخدمات المناطق الصناعية وتمويل المؤسسات الصغيرة والمتوسطة والتصنيع المحلي.", "Rétablir durablement la production et renforcer la valeur ajoutée locale.", "استعادة الإنتاج بصورة مستدامة وتعزيز القيمة المضافة المحلية.", "medium"),
    "structural": ("Diversifier la base productive et renforcer la résilience", "تنويع القاعدة الإنتاجية وتعزيز المرونة", "Développer l’industrie non extractive, la transformation agricole et halieutique, la logistique et les services numériques, avec une énergie et une finance plus résilientes.", "تطوير الصناعة غير الاستخراجية وتحويل المنتجات الزراعية والسمكية والخدمات اللوجستية والرقمية مع طاقة وتمويل أكثر مرونة.", "Réduire la concentration et la vulnérabilité aux chocs futurs.", "خفض التركّز والهشاشة أمام الصدمات المستقبلية.", "medium"),
}

def _confidence_reason(confidence: str) -> tuple[str, str]:
    if confidence == "low": return "Des informations importantes sont manquantes.", "توجد معلومات مهمة غير متاحة."
    if confidence == "high": return "Les données comptables sont complètes et l’action est limitée au suivi de continuité.", "البيانات المحاسبية مكتملة والإجراء يقتصر على متابعة الاستمرارية."
    return "L’option concorde avec le poids et l’historique du secteur, mais les données d’emploi et d’entreprise sont indisponibles.", "يتسق الخيار مع وزن القطاع وتاريخه، لكن بيانات التشغيل والمؤسسات غير متاحة."

def _item(sector: str, horizon: str, metrics: list[dict], confidence: str, fallback: bool) -> dict:
    title_fr, title_ar, description_fr, description_ar, objective_fr, objective_ar, priority = HORIZON_ACTIONS[horizon]
    confidence_fr, confidence_ar = _confidence_reason(confidence)
    return {"code": f"{'fallback' if fallback else sector}_{horizon}_v1", "title_fr": title_fr, "title_ar": title_ar,
        "description_fr": description_fr, "description_ar": description_ar, "time_horizon": horizon, "priority": priority,
        "sector_codes": [sector], "reason_fr": "L’impact comptable direct et le poids observé du secteur justifient cette option à cet horizon.",
        "reason_ar": "يبرر الأثر المحاسبي المباشر والوزن المرصود للقطاع هذا الخيار ضمن هذا الأفق.", "supporting_metrics": metrics,
        "responsible_actor_categories": ["public_authorities", "sector_operators", "financial_institutions"],
        "implementation_steps_fr": ["Valider les besoins avec les opérateurs concernés.", "Définir un responsable, une échéance et un indicateur de suivi."],
        "implementation_steps_ar": ["التحقق من الاحتياجات مع المشغلين المعنيين.", "تحديد مسؤول وأجل ومؤشر للمتابعة."],
        "monitoring_indicators": MONITORING.get(sector, [sector, "gdp_activity_market_prices"]),
        "escalation_trigger_fr": "Escalader si la production ou l’accès aux intrants continue de se dégrader.",
        "escalation_trigger_ar": "التصعيد إذا استمر تراجع الإنتاج أو الوصول إلى المدخلات.",
        "expected_objective_fr": objective_fr, "expected_objective_ar": objective_ar, "confidence": confidence,
        "confidence_reason_fr": confidence_fr, "confidence_reason_ar": confidence_ar,
        "limitations_fr": LIMIT_FR, "limitations_ar": LIMIT_AR}

def catalogue_for(sector: str, risk: str = "high", confidence: str = "moderate", metrics: list[dict] | None = None, *, fallback: bool = False) -> list[dict]:
    known = sector in KNOWN_SECTORS
    if not known and not fallback: return []
    return [_item(sector, horizon, metrics or [], "high" if confidence == "high" and horizon == "immediate" else ("low" if confidence == "low" else "moderate"), not known)
            for horizon in ("immediate", "stabilization", "recovery", "structural")]

def _alternatives(db: Session, year: int, affected: list[str]) -> list[dict]:
    gdp = get_ok_series(db, "gdp_activity_market_prices"); rows = []
    candidates = ["agriculture_forestry", "livestock_hunting", "fishing", "extractive_activities", "manufacturing", "construction_public_works", "commerce", "transport", "information_communication", "other_services"]
    for code in candidates:
        if code in affected or year not in gdp: continue
        ind, series = get_indicator_or_404(db, code), get_ok_series(db, code)
        if year not in series: continue
        rates = growth_rates(series); completeness = len(series) / (max(series) - min(series) + 1) * 100
        avg = mean(rates.values()) if rates else None; vol = pstdev(rates.values()) if len(rates) > 1 else None; recent = rates.get(year); share = series[year] / gdp[year] * 100
        score = alternative_score(historical_growth_pct=avg, volatility_pct=vol, recent_growth_pct=recent, completeness_pct=completeness, gdp_share_pct=share)
        rows.append((score, {"indicator_code": code, "name_fr": ind.name_fr, "name_ar": ind.name_ar, "gdp_share_pct": share, "historical_growth_pct": avg, "recent_growth_pct": recent, "volatility_pct": vol,
          "reason_fr": "Classement combinant poids, croissance, stabilité, dynamique récente et complétude.", "reason_ar": "ترتيب يجمع الوزن والنمو والاستقرار والديناميكية الحديثة واكتمال البيانات.",
          "confidence": confidence_from_completeness(completeness), "limitation_fr": LIMIT_FR, "limitation_ar": LIMIT_AR}))
    return [row for _, row in sorted(rows, key=lambda x: x[0], reverse=True)[:4]]

def _canonical_with_parent(db: Session, code: str) -> tuple[str, str | None]:
    indicator = get_indicator_or_404(db, code)
    canonical = indicator.alias_of if indicator.is_alias and indicator.alias_of else indicator
    return canonical.code, canonical.parent.code if canonical.parent else None

def generate(db: Session, year: int, shocks: list[dict], duration: str, **options) -> dict:
    result = stress_test.multiple(db, year, shocks); affected = [e["indicator_code"] for e in result["individual_effects"]]
    histories = [stress_test.history(db, code, None, year) for code in affected]
    volatilities = [pstdev(r.values()) for code in affected if len((r := growth_rates(get_ok_series(db, code)))) > 1]
    concentration = stress_test.concentration(db, year, "main_sectors")
    recent_negative = any(h["points"] and h["points"][-1]["nominal_growth_contribution_pct"] is not None and h["points"][-1]["nominal_growth_contribution_pct"] < 0 for h in histories)
    risk = classify_risk(result["total_direct_gdp_impact_pct"], volatility_pct=max(volatilities) if volatilities else None,
        largest_sector_share_pct=max(e["sector_share_of_gdp_pct"] for e in result["individual_effects"]), largest_shock_rate=max(s["shock_rate"] for s in shocks),
        duration=duration, combined_shocks=len(shocks), concentration_hhi=concentration["hhi"], recent_negative_growth=recent_negative)
    recommendations = []
    for effect in result["individual_effects"]:
        canonical, parent = _canonical_with_parent(db, effect["indicator_code"])
        selected = canonical if canonical in KNOWN_SECTORS else parent if parent in KNOWN_SECTORS else canonical
        history = next((h for h in histories if h["indicator_code"] == effect["indicator_code"]), None)
        completeness = 100 * len(history["points"]) / (history["end_year"] - history["start_year"] + 1) if history else None
        confidence = confidence_from_completeness(completeness)
        metrics = [{"label_fr": "Taux de choc", "label_ar": "نسبة الصدمة", "value": effect["shock_rate"] * 100, "unit": "%"},
          {"label_fr": "Impact direct sur le PIB", "label_ar": "الأثر المباشر على الناتج", "value": effect["direct_gdp_impact_pct"], "unit": "%"},
          {"label_fr": "Part du secteur dans le PIB", "label_ar": "حصة القطاع من الناتج", "value": effect["sector_share_of_gdp_pct"], "unit": "%"}]
        recommendations.extend(catalogue_for(selected, risk, confidence, metrics, fallback=selected not in KNOWN_SECTORS))
    unique = {r["code"]: r for r in recommendations}
    limited = [r for horizon in HORIZON_ACTIONS for r in list(x for x in unique.values() if x["time_horizon"] == horizon)[:2]]
    monitoring = sorted({code for rec in limited for code in rec["monitoring_indicators"]})
    return {"year": year, "risk_level": risk, "risk_basis_fr": "Risque expérimental distinct de la priorité des actions, fondé sur l’impact direct et les vulnérabilités observées.",
      "risk_basis_ar": "خطر تجريبي منفصل عن أولوية الإجراءات، يستند إلى الأثر المباشر ومواطن الهشاشة المرصودة.", "stress_test": result,
      "recommendations": limited, "alternative_sectors": _alternatives(db, year, affected), "monitoring_indicators": monitoring,
      "disclaimer_fr": DISCLAIMER_FR, "disclaimer_ar": DISCLAIMER_AR, "thresholds_disclaimer_fr": THRESHOLDS_FR, "thresholds_disclaimer_ar": THRESHOLDS_AR,
      "source": stress_test.SOURCE, "unit": stress_test.UNIT}
