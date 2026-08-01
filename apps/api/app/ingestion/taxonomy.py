"""Canonical indicator taxonomy for the two real ANSADE/CN source files.

Mirrors docs/DATA_DICTIONARY.md exactly, verified against the actual
workbook contents. Because both files have a fixed, known row order (one
indicator per row, always in the same position), the importer maps rows to
indicators **positionally**, not by fuzzy text matching — this is robust
against the source's own inconsistent spelling/numbering/spacing
("Administations" vs "Administrations", "brut" vs "brute", "éléctricité" vs
"électricité", "travauxpublics" with no space, etc.). Each row spec below
still carries a short normalized fragment used only as a defensive sanity
check that the file hasn't shifted rows.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorRowSpec:
    code: str
    name_fr: str
    name_ar: str
    hierarchy_level: int
    parent_code: str | None
    category: str  # aggregate | sector | subsector | component | flow
    source_side: str  # expenditure | activity
    is_aggregate: bool = False
    is_alias: bool = False
    alias_of_code: str | None = None
    label_fragment: str = ""  # normalized substring expected in the raw source label

    def __post_init__(self):
        if not self.label_fragment:
            object.__setattr__(self, "label_fragment", _default_fragment(self.name_fr))


def _default_fragment(name_fr: str) -> str:
    from app.ingestion.normalize import normalize_text

    return normalize_text(name_fr)


# --- File A: comptes_nationaux_4.9.1.xlsx, sheet "Emplos du PIB courant " ---
# Rows 4-15 in that exact order (source row -> spec index).
EXPENDITURE_ROWS: tuple[IndicatorRowSpec, ...] = (
    IndicatorRowSpec("imports", "Importation", "الواردات", 1, None, "flow", "expenditure"),
    IndicatorRowSpec("gdp_expenditure", "PIB", "الناتج المحلي الإجمالي (حسب الإنفاق)", 1, None, "aggregate", "expenditure", is_aggregate=True, label_fragment="pib"),
    IndicatorRowSpec("final_consumption", "Consommation Finale", "الاستهلاك النهائي", 1, None, "aggregate", "expenditure", is_aggregate=True),
    IndicatorRowSpec("household_final_consumption", "Consommation Finale Ménage", "الاستهلاك النهائي للأسر", 2, "final_consumption", "component", "expenditure"),
    IndicatorRowSpec("household_nonmarket_consumption", "Consommation Finale Ménage non marchande", "الاستهلاك النهائي غير السوقي للأسر", 3, "household_final_consumption", "component", "expenditure"),
    IndicatorRowSpec("household_market_consumption", "Consommation Finale Ménage marchande", "الاستهلاك النهائي السوقي للأسر", 3, "household_final_consumption", "component", "expenditure"),
    IndicatorRowSpec("government_final_consumption", "Consommation Finale des Administrations Publiques", "الاستهلاك النهائي للإدارات العمومية", 2, "final_consumption", "component", "expenditure", label_fragment="consommation finale des admin"),
    IndicatorRowSpec("isblm_final_consumption", "Consommation Finale des ISBLM", "الاستهلاك النهائي للمؤسسات غير الهادفة للربح", 2, "final_consumption", "component", "expenditure"),
    IndicatorRowSpec("gross_fixed_capital_formation", "Formation brute de capital fixe", "التكوين الإجمالي لرأس المال الثابت", 1, None, "flow", "expenditure", label_fragment="formation brut"),
    IndicatorRowSpec("inventory_changes", "Variations de stock", "تغير المخزونات", 1, None, "flow", "expenditure"),
    IndicatorRowSpec("net_acquisition_valuables", "Acquisitions nettes en objets de valeur", "صافي اقتناء الأشياء الثمينة", 1, None, "flow", "expenditure"),
    IndicatorRowSpec("exports", "Exportation", "الصادرات", 1, None, "flow", "expenditure"),
)

# --- File B: comptes_nationaux_4.9.2.xlsx, sheet "PIB Courant (2)" ---
# Rows 4-30 in that exact order.
ACTIVITY_ROWS: tuple[IndicatorRowSpec, ...] = (
    IndicatorRowSpec("primary_sector", "Secteur primaire", "القطاع الأولي", 1, None, "sector", "activity"),
    IndicatorRowSpec("agriculture_fishing_forestry", "Agriculture, pêche, exploitation forestière", "الزراعة والصيد واستغلال الغابات", 2, "primary_sector", "subsector", "activity", is_alias=True, alias_of_code="primary_sector"),
    IndicatorRowSpec("agriculture_forestry", "Agriculture, Sylviculture et Exploitation Forestière", "الزراعة والحراجة واستغلال الغابات", 3, "agriculture_fishing_forestry", "subsector", "activity", label_fragment="agriculture sylviculture"),
    IndicatorRowSpec("livestock_hunting", "Elevage et chasse", "تربية الماشية والصيد البري", 3, "agriculture_fishing_forestry", "subsector", "activity"),
    IndicatorRowSpec("fishing", "Pêche", "الصيد البحري", 3, "agriculture_fishing_forestry", "subsector", "activity"),
    IndicatorRowSpec("secondary_sector", "Secteur secondaire", "القطاع الثانوي", 1, None, "sector", "activity"),
    IndicatorRowSpec("extractive_activities", "Activités extractives", "الأنشطة الاستخراجية", 2, "secondary_sector", "subsector", "activity"),
    IndicatorRowSpec("oil_gas_extraction", "Extraction de produits pétroliers et gaziers", "استخراج المنتجات البترولية والغازية", 3, "extractive_activities", "subsector", "activity"),
    IndicatorRowSpec("non_oil_extractive_activities", "Industries extractives hors pétrole et gaz", "الأنشطة الاستخراجية غير النفطية والغازية", 3, "extractive_activities", "subsector", "activity", label_fragment="industries extractives autre"),
    IndicatorRowSpec("metallic_mineral_extraction", "Extraction des minerais métalliques", "استخراج المعادن الفلزية", 4, "non_oil_extractive_activities", "subsector", "activity", label_fragment="extraction des minerais met"),
    IndicatorRowSpec("snim_iron", "Fer SNIM", "حديد سنيم", 5, "metallic_mineral_extraction", "subsector", "activity", label_fragment="fer_snim"),
    IndicatorRowSpec("gold_copper", "Or et Cuivre", "الذهب والنحاس", 5, "metallic_mineral_extraction", "subsector", "activity"),
    IndicatorRowSpec("other_extractive_activities", "Autres activités extractives", "الأنشطة الاستخراجية الأخرى", 4, "non_oil_extractive_activities", "subsector", "activity"),
    IndicatorRowSpec("manufacturing", "Activités manufacturières", "الأنشطة الصناعية التحويلية", 2, "secondary_sector", "subsector", "activity"),
    IndicatorRowSpec("manufacturing_excluding_water_electricity", "Activités manufacturières hors eau et électricité", "الأنشطة الصناعية التحويلية باستثناء الماء والكهرباء", 3, "manufacturing", "subsector", "activity", label_fragment="activites manufacturieres hors eau"),
    IndicatorRowSpec("water_electricity", "Production et distribution d'eau et d'électricité", "إنتاج وتوزيع الماء والكهرباء", 3, "manufacturing", "subsector", "activity", label_fragment="production et distribution d"),
    IndicatorRowSpec("construction_public_works", "Bâtiment et travaux publics", "البناء والأشغال العمومية", 2, "secondary_sector", "subsector", "activity", label_fragment="batiment et travaux"),
    IndicatorRowSpec("tertiary_sector", "Secteur tertiaire", "القطاع الثالثي", 1, None, "sector", "activity"),
    IndicatorRowSpec("transport_information_communication", "Transport, Information et communication", "النقل والإعلام والاتصال", 2, "tertiary_sector", "subsector", "activity"),
    IndicatorRowSpec("transport", "Transport", "النقل", 3, "transport_information_communication", "subsector", "activity"),
    IndicatorRowSpec("information_communication", "Information et communication", "الإعلام والاتصال", 3, "transport_information_communication", "subsector", "activity"),
    IndicatorRowSpec("commerce", "Commerce", "التجارة", 2, "tertiary_sector", "subsector", "activity"),
    IndicatorRowSpec("other_services", "Autres services", "خدمات أخرى", 2, "tertiary_sector", "subsector", "activity"),
    IndicatorRowSpec("public_administration", "Administrations publiques", "الإدارة العامة", 2, "tertiary_sector", "subsector", "activity"),
    IndicatorRowSpec("gdp_factor_cost", "PIB au coût des facteurs", "الناتج المحلي الإجمالي بتكلفة عناصر الإنتاج", 1, None, "aggregate", "activity", is_aggregate=True, label_fragment="p.i.b. au cout des facteurs"),
    IndicatorRowSpec("net_taxes_products", "Taxes nettes sur les produits", "الضرائب الصافية على المنتجات", 1, None, "aggregate", "activity", is_aggregate=True),
    IndicatorRowSpec("gdp_activity_market_prices", "PIB aux prix du marché", "الناتج المحلي الإجمالي بأسعار السوق", 1, None, "aggregate", "activity", is_aggregate=True, label_fragment="p.i.b. aux prix du marche"),
)


def all_rows() -> tuple[IndicatorRowSpec, ...]:
    return EXPENDITURE_ROWS + ACTIVITY_ROWS


def by_code(code: str) -> IndicatorRowSpec | None:
    for row in all_rows():
        if row.code == code:
            return row
    return None
