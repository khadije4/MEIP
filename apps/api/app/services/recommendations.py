from __future__ import annotations

from statistics import mean, pstdev

from sqlalchemy.orm import Session

from app.analytics.recommendations import alternative_score, classify_risk, confidence_from_completeness
from app.analytics.stress_test import growth_rates
from app.services.series import get_indicator_or_404, get_ok_series
from app.services import stress_test

DISCLAIMER_FR = "Les recommandations sont des options de réponse fondées sur les comptes nationaux disponibles. Elles ne remplacent pas une étude sectorielle, budgétaire, sociale ou environnementale détaillée."
DISCLAIMER_AR = "تمثل التوصيات خيارات استجابة مبنية على بيانات الحسابات الوطنية المتاحة، ولا تعوض دراسة قطاعية أو مالية أو اجتماعية أو بيئية مفصلة."
THRESHOLDS_FR = "Les seuils de risque sont expérimentaux et définis par la plateforme; ils ne constituent pas des normes officielles du gouvernement."
THRESHOLDS_AR = "عتبات المخاطر تجريبية وتحددها المنصة؛ وهي ليست معايير حكومية رسمية."
LIMIT_FR = "Option à valider par des études sectorielles, budgétaires, sociales et environnementales; aucun coût ni effet sur l’emploi n’est estimé."
LIMIT_AR = "خيار يتطلب التحقق بدراسات قطاعية ومالية واجتماعية وبيئية؛ ولا يتضمن تقديراً للتكلفة أو أثر التشغيل."

SECTOR_ACTIONS = {
 "primary_sector": ("Protéger les chaînes alimentaires et rurales", "حماية سلاسل الغذاء والريف"),
 "agriculture_forestry": ("Sécuriser l’eau, les intrants, la logistique et le stockage", "تأمين المياه والمدخلات والخدمات اللوجستية والتخزين"),
 "livestock_hunting": ("Protéger l’accès à l’eau, aux aliments et aux services vétérinaires", "حماية الوصول إلى المياه والأعلاف والخدمات البيطرية"),
 "fishing": ("Protéger la chaîne du froid et diversifier les marchés et la transformation locale", "حماية سلسلة التبريد وتنويع الأسواق والتصنيع المحلي"),
 "secondary_sector": ("Préserver les infrastructures et capacités productives critiques", "الحفاظ على البنية التحتية والقدرات الإنتاجية الحيوية"),
 "extractive_activities": ("Préserver les infrastructures critiques et évaluer les risques fournisseurs, exportations et recettes publiques", "حماية البنية التحتية الحيوية وتقييم مخاطر الموردين والصادرات والإيرادات العامة"),
 "oil_gas_extraction": ("Sécuriser les installations et les mécanismes de continuité", "تأمين المنشآت وآليات استمرارية النشاط"),
 "snim_iron": ("Préserver les corridors miniers et renforcer la transformation locale", "حماية الممرات التعدينية وتعزيز التصنيع المحلي"),
 "gold_copper": ("Protéger les opérations essentielles et suivre les risques d’exportation", "حماية العمليات الأساسية ومراقبة مخاطر الصادرات"),
 "manufacturing": ("Sécuriser l’électricité, l’eau, la maintenance et le fonds de roulement", "تأمين الكهرباء والمياه والصيانة ورأس المال العامل"),
 "water_electricity": ("Garantir la continuité des services d’eau et d’électricité", "ضمان استمرارية خدمات المياه والكهرباء"),
 "construction_public_works": ("Prioriser les projets à fort impact et accélérer les paiements vérifiés", "إعطاء الأولوية للمشاريع عالية الأثر وتسريع المدفوعات المتحقق منها"),
 "tertiary_sector": ("Préserver la continuité des services essentiels", "الحفاظ على استمرارية الخدمات الأساسية"),
 "commerce": ("Protéger la distribution essentielle et l’accès temporaire au fonds de roulement", "حماية التوزيع الأساسي والوصول المؤقت إلى رأس المال العامل"),
 "transport": ("Protéger les corridors critiques et la logistique des biens essentiels", "حماية الممرات الحيوية ولوجستيات السلع الأساسية"),
 "information_communication": ("Protéger les télécommunications, la cybersécurité et la reprise après sinistre", "حماية الاتصالات والأمن السيبراني والتعافي من الكوارث"),
 "other_services": ("Maintenir les services essentiels et soutenir les opérateurs viables", "الحفاظ على الخدمات الأساسية ودعم المشغلين القابلين للاستمرار"),
 "public_administration": ("Assurer la continuité des services publics prioritaires", "ضمان استمرارية الخدمات العامة ذات الأولوية"),
}

MONITORING = {
 "extractive_activities": ["exports", "extractive_activities", "gdp_activity_market_prices"],
 "fishing": ["fishing", "exports", "gdp_activity_market_prices"],
 "commerce": ["commerce", "imports", "final_consumption"],
 "construction_public_works": ["construction_public_works", "gross_fixed_capital_formation"],
 "transport": ["transport", "imports", "exports"],
}

def _item(code: str, sector: str, horizon: str, priority: str, metrics: list[str], confidence: str) -> dict:
    title_fr, title_ar = SECTOR_ACTIONS.get(sector, SECTOR_ACTIONS["primary_sector"])
    suffix_fr = {"immediate":"Action immédiate", "stabilization":"Stabilisation", "recovery":"Relance", "structural":"Résilience structurelle"}[horizon]
    suffix_ar = {"immediate":"إجراء فوري", "stabilization":"استقرار", "recovery":"تعافٍ", "structural":"مرونة هيكلية"}[horizon]
    return {"code": code, "title_fr": f"{suffix_fr} — {title_fr}", "title_ar": f"{suffix_ar} — {title_ar}",
      "description_fr": title_fr + ".", "description_ar": title_ar + ".", "time_horizon": horizon, "priority": priority,
      "sector_codes": [sector], "reason_fr": "Le choc comptable direct et les caractéristiques historiques du secteur justifient l’examen de cette option.",
      "reason_ar": "تبرر الصدمة المحاسبية المباشرة والخصائص التاريخية للقطاع دراسة هذا الخيار.", "supporting_metrics": metrics,
      "monitoring_indicators": MONITORING.get(sector, [sector, "gdp_activity_market_prices"]),
      "expected_objective_fr": "Préserver les fonctions essentielles puis réduire la vulnérabilité au choc.",
      "expected_objective_ar": "الحفاظ على الوظائف الأساسية ثم تقليل التعرض للصدمة.", "confidence": confidence,
      "limitations_fr": LIMIT_FR, "limitations_ar": LIMIT_AR}

def catalogue_for(sector: str, risk: str = "high", confidence: str = "moderate", metrics: list[str] | None = None) -> list[dict]:
    if sector not in SECTOR_ACTIONS: return []
    horizons = ["immediate", "stabilization", "recovery", "structural"] if risk in ("high", "critical") else (["stabilization", "recovery", "structural"] if risk == "moderate" else ["recovery", "structural"])
    priority = {"low":"low", "moderate":"medium", "high":"high", "critical":"critical"}[risk]
    return [_item(f"{sector}_{horizon}", sector, horizon, priority, metrics or [], confidence) for horizon in horizons]

def _alternatives(db: Session, year: int, affected: list[str]) -> list[dict]:
    gdp = get_ok_series(db, "gdp_activity_market_prices")
    candidates = ["agriculture_forestry", "livestock_hunting", "fishing", "extractive_activities", "manufacturing", "construction_public_works", "commerce", "transport", "information_communication", "other_services"]
    rows = []
    for code in candidates:
        if code in affected or year not in gdp: continue
        ind, series = get_indicator_or_404(db, code), get_ok_series(db, code)
        if year not in series: continue
        rates = growth_rates(series); expected = max(series)-min(series)+1
        completeness = len(series)/expected*100
        avg = mean(rates.values()) if rates else None; vol = pstdev(rates.values()) if len(rates)>1 else None
        recent = rates.get(year); share = series[year]/gdp[year]*100
        score = alternative_score(historical_growth_pct=avg, volatility_pct=vol, recent_growth_pct=recent, completeness_pct=completeness, gdp_share_pct=share)
        confidence = confidence_from_completeness(completeness)
        rows.append((score, {"indicator_code":code,"name_fr":ind.name_fr,"name_ar":ind.name_ar,"gdp_share_pct":share,
          "historical_growth_pct":avg,"recent_growth_pct":recent,"volatility_pct":vol,
          "reason_fr":"Sélection équilibrant poids économique, croissance, stabilité, dynamique récente et complétude; elle ne repose pas sur la seule croissance.",
          "reason_ar":"اختيار يوازن الوزن الاقتصادي والنمو والاستقرار والديناميكية الحديثة واكتمال البيانات؛ ولا يعتمد على النمو وحده.",
          "confidence":confidence,"limitation_fr":"Ce classement ne mesure pas l’emploi, la rentabilité, le coût d’investissement ni la faisabilité environnementale ou régionale.",
          "limitation_ar":"لا يقيس هذا التصنيف خلق فرص العمل أو الربحية أو تكلفة الاستثمار أو الجدوى البيئية أو الجهوية."}))
    return [row for _, row in sorted(rows, key=lambda x:x[0], reverse=True)[:4]]

def generate(db: Session, year: int, shocks: list[dict], duration: str, **options) -> dict:
    result = stress_test.multiple(db, year, shocks)
    affected = [effect["indicator_code"] for effect in result["individual_effects"]]
    histories = [stress_test.history(db, code, None, year) for code in affected]
    volatilities=[]
    for code in affected:
        rates=growth_rates(get_ok_series(db, code))
        if len(rates)>1: volatilities.append(pstdev(rates.values()))
    concentration = stress_test.concentration(db, year, "main_sectors")
    recent_negative=any((h["points"] and h["points"][-1]["nominal_growth_contribution_pct"] is not None and h["points"][-1]["nominal_growth_contribution_pct"] < 0) for h in histories)
    risk=classify_risk(result["total_direct_gdp_impact_pct"],volatility_pct=max(volatilities) if volatilities else None,
      largest_sector_share_pct=max(e["sector_share_of_gdp_pct"] for e in result["individual_effects"]),largest_shock_rate=max(s["shock_rate"] for s in shocks),
      duration=duration,combined_shocks=len(shocks),concentration_hhi=concentration["hhi"],recent_negative_growth=recent_negative)
    recommendations=[]
    for effect in result["individual_effects"]:
        completeness=next((h for h in histories if h["indicator_code"]==effect["indicator_code"]),None)
        confidence=confidence_from_completeness(100*(len(completeness["points"])/(completeness["end_year"]-completeness["start_year"]+1)) if completeness else None)
        metrics=[f"direct_gdp_impact_pct={effect['direct_gdp_impact_pct']:.4f}",f"sector_share_pct={effect['sector_share_of_gdp_pct']:.4f}",f"shock_rate={effect['shock_rate']:.4f}"]
        recommendations.extend(catalogue_for(effect["indicator_code"],risk,confidence,metrics))
    monitoring=sorted({item for rec in recommendations for item in rec["monitoring_indicators"]})
    return {"year":year,"risk_level":risk,"risk_basis_fr":"Classification expérimentale fondée sur l’impact direct, le choc, la durée, la volatilité, la concentration et la dynamique récente.",
      "risk_basis_ar":"تصنيف تجريبي يستند إلى الأثر المباشر وحجم الصدمة ومدتها والتقلب والتركيز والديناميكية الحديثة.","stress_test":result,
      "recommendations":recommendations,"alternative_sectors":_alternatives(db,year,affected),"monitoring_indicators":monitoring,
      "disclaimer_fr":DISCLAIMER_FR,"disclaimer_ar":DISCLAIMER_AR,"thresholds_disclaimer_fr":THRESHOLDS_FR,"thresholds_disclaimer_ar":THRESHOLDS_AR,
      "source":stress_test.SOURCE,"unit":stress_test.UNIT}

