import re
import pytest


@pytest.fixture()
def recommendation_client(client, real_data_raw_dir):
    for name in ("comptes_nationaux_4.9.1.xlsx", "comptes_nationaux_4.9.2.xlsx"):
        if not (real_data_raw_dir / name).exists(): pytest.skip("Real workbooks are required")
    assert client.post("/api/data/import").status_code==200
    return client


@pytest.mark.parametrize("sector,rate",[("extractive_activities",1),("fishing",.5),("agriculture_forestry",.3),("construction_public_works",.3),("commerce",.25)])
def test_sector_scenarios_are_bilingual_and_specific(recommendation_client,sector,rate):
    response=recommendation_client.post("/api/recommendations/generate",json={"year":2024,"shocks":[{"indicator_code":sector,"shock_rate":rate}],"shock_duration":"one_year"})
    assert response.status_code==200,response.text
    body=response.json(); assert body["risk_level"] in ("low","moderate","high","critical")
    assert body["disclaimer_fr"] and body["disclaimer_ar"] and body["thresholds_disclaimer_fr"]
    assert body["recommendations"] and all(r["title_fr"] and r["title_ar"] for r in body["recommendations"])
    assert len({r["code"] for r in body["recommendations"]})==len(body["recommendations"])


def test_combined_high_risk_has_every_horizon_and_alternatives(recommendation_client):
    shocks=[{"indicator_code":"extractive_activities","shock_rate":1},{"indicator_code":"fishing","shock_rate":1},{"indicator_code":"commerce","shock_rate":1},{"indicator_code":"transport","shock_rate":1}]
    body=recommendation_client.post("/api/recommendations/generate",json={"year":2024,"shocks":shocks,"shock_duration":"multi_year"}).json()
    assert body["risk_level"] in ("high","critical")
    assert {r["time_horizon"] for r in body["recommendations"]}=={"immediate","stabilization","recovery","structural"}
    assert body["alternative_sectors"]
    assert all(a["limitation_fr"] and a["limitation_ar"] for a in body["alternative_sectors"])


def test_catalogue_monitoring_and_no_unsupported_numeric_claims(recommendation_client):
    catalogue=recommendation_client.get("/api/recommendations/catalogue")
    assert catalogue.status_code==200; assert len(catalogue.json())>=18
    sector=recommendation_client.get("/api/recommendations/sectors/fishing").json()
    assert sector["recommendations"] and sector["monitoring_indicators"]
    monitoring=recommendation_client.get("/api/recommendations/monitoring-indicators/fishing").json()
    assert "fishing" in monitoring["indicator_codes"]
    prose=" ".join(r["description_fr"]+" "+r["description_ar"] for r in sector["recommendations"])
    assert not re.search(r"\b\d+(?:[.,]\d+)?\s*(?:MRU|emplois?|millions?|milliards?)\b",prose,re.I)

