"""Bilingual natural-language indicator resolution for the assistant."""
from __future__ import annotations
import re
import unicodedata

ALIASES: dict[str, tuple[str, ...]] = {
    "gdp_activity_market_prices": ("pib", "produit interieur brut", "الناتج المحلي الاجمالي", "الناتج المحلي"),
    "extractive_activities": ("activites extractives", "secteur extractif", "الاستخراجية", "الاستخراج"),
    "primary_sector": ("secteur primaire", "القطاع الاولي"), "secondary_sector": ("secteur secondaire", "القطاع الثانوي"),
    "tertiary_sector": ("secteur tertiaire", "القطاع الثالثي"), "fishing": ("peche", "الصيد"),
    "commerce": ("commerce", "التجارة"), "construction_public_works": ("btp", "batiment", "travaux publics", "البناء", "الاشغال العامة"),
    "snim_iron": ("snim", "fer", "سنيم", "الحديد"), "gold_copper": ("or et cuivre", "or et le cuivre", "الذهب والنحاس"),
    "exports": ("exportations", "الصادرات"), "imports": ("importations", "الواردات"),
}

def normalize(text: str) -> str:
    value=unicodedata.normalize("NFKD", text.lower().replace("’", "'"))
    return re.sub(r"\s+", " ", "".join(c for c in value if not unicodedata.combining(c))).strip()

def resolve_indicators(question: str) -> list[str]:
    normalized=normalize(question)
    matches=[(normalized.find(alias),-len(alias),code) for code,aliases in ALIASES.items() for alias in aliases if alias in normalized]
    return list(dict.fromkeys(code for _,_,code in sorted(matches)))
