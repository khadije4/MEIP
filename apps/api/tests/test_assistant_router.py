from app.services.assistant_router import route_question
from app.services.indicator_resolver import resolve_indicators

def test_routes_multi_capability_free_text_question():
    routed=route_question("Comparez la pêche et les activités extractives entre 2010 et 2024")
    assert "comparison" in routed.capabilities
    assert routed.indicators == ("fishing","extractive_activities")
    assert routed.years == (2010,2024)

def test_resolves_arabic_and_spelling_variants():
    assert resolve_indicators("قارن التجارة مع البناء والأشغال العامة") == ["commerce","construction_public_works"]
    assert resolve_indicators("Évolution du fer SNIM") == ["snim_iron"]
