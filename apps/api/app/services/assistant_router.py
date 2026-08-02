"""Multi-capability, non-whitelist routing signals for free-text questions."""
from __future__ import annotations
import re
from dataclasses import dataclass
from app.services.indicator_resolver import normalize, resolve_indicators

@dataclass(frozen=True)
class AssistantRoute:
    capabilities: tuple[str,...]
    indicators: tuple[str,...]
    years: tuple[int,...]

def route_question(question: str) -> AssistantRoute:
    q=normalize(question); capabilities=[]
    rules={
      "methodology":("source","methode","methodologie","prix courants","valeurs manquantes","مصدر","منهج","الاسعار الجارية"),
      "forecast":("prevision","prevoir","forecast","توقع"),"scenario":("si ","choc","baisse de","arrete","سيناريو","صدمة","انخفض"),
      "comparison":("compare","difference","versus","قارن","الفرق"),"volatility":("volatil","تقلب"),"growth":("croissance","evolu","نمو","تطور"),
      "ranking":("plus grand","classe","rang","اكبر","رتب"),"trade_balance":("solde commercial","balance commerciale","الميزان التجاري"),
      "dataset_overview":("donnees disponibles","indicateurs disponibles","derniere annee","البيانات المتاحة","المؤشرات المتاحة","اخر سنة"),
      "general_economic_explanation":("qu'est-ce","pourquoi","explique","ما هو","لماذا","اشرح"),
    }
    for capability,terms in rules.items():
        if any(term in q for term in terms): capabilities.append(capability)
    if not capabilities: capabilities.append("latest_value" if resolve_indicators(q) else "unsupported_data_request")
    return AssistantRoute(tuple(capabilities),tuple(resolve_indicators(q)),tuple(int(y) for y in re.findall(r"(?:19|20)\d{2}",q)))
