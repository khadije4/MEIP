import pytest


@pytest.fixture()
def stress_client(client, real_data_raw_dir):
    for name in ("comptes_nationaux_4.9.1.xlsx", "comptes_nationaux_4.9.2.xlsx"):
        if not (real_data_raw_dir / name).exists(): pytest.skip("Real workbooks are required")
    assert client.post("/api/data/import").status_code == 200
    return client


@pytest.mark.parametrize("rate", [0, 0.1, 0.5, 1.0])
def test_single_shock_formula_and_shutdown_share(stress_client, rate):
    response=stress_client.post("/api/stress-test/single",json={"year":2024,"indicator_code":"fishing","shock_rate":rate})
    assert response.status_code==200,response.text
    body=response.json()
    assert body["simulated_gdp"]==pytest.approx(body["baseline_activity_gdp"]-body["direct_loss"])
    assert body["direct_loss"]==pytest.approx(body["sector_value"]*rate)
    if rate==1: assert body["direct_gdp_impact_pct"]==pytest.approx(body["sector_share_of_gdp_pct"])
    assert body["methodology_disclaimer_fr"] and body["methodology_disclaimer_ar"]


def test_invalid_rates_unknown_indicator_year_and_missing_value(stress_client):
    for rate in (-0.1,1.1):
        assert stress_client.post("/api/stress-test/single",json={"year":2024,"indicator_code":"fishing","shock_rate":rate}).status_code==422
    assert stress_client.post("/api/stress-test/single",json={"year":2024,"indicator_code":"unknown","shock_rate":.5}).status_code==404
    assert stress_client.post("/api/stress-test/single",json={"year":1900,"indicator_code":"fishing","shock_rate":.5}).status_code==422
    response=stress_client.post("/api/stress-test/single",json={"year":2023,"indicator_code":"oil_gas_extraction","shock_rate":.5})
    assert response.status_code==400
    assert response.json()["error"]["code"]=="value_not_available"


def test_multiple_no_double_count_and_hierarchy_alias_conflicts(stress_client):
    payload={"year":2024,"shocks":[{"indicator_code":"fishing","shock_rate":.5},{"indicator_code":"commerce","shock_rate":.25}]}
    response=stress_client.post("/api/stress-test/multiple",json=payload)
    assert response.status_code==200,response.text
    body=response.json(); assert body["hierarchy_validation"]=="valid"
    assert body["total_direct_loss"]==pytest.approx(sum(e["direct_loss"] for e in body["individual_effects"]))
    conflicts=[("primary_sector","fishing"),("extractive_activities","snim_iron"),("agriculture_fishing_forestry","fishing")]
    for parent,child in conflicts:
        conflict=stress_client.post("/api/stress-test/multiple",json={"year":2024,"shocks":[{"indicator_code":parent,"shock_rate":.2},{"indicator_code":child,"shock_rate":.2}]})
        assert conflict.status_code==400,conflict.text
        assert conflict.json()["error"]["code"]=="hierarchy_conflict"


def test_ranking_dependency_concentration_and_presets(stress_client):
    ranking=stress_client.get("/api/stress-test/ranking",params={"year":2024,"ranking_group":"main_sectors"})
    assert ranking.status_code==200; assert [x["vulnerability_rank"] for x in ranking.json()["sectors"]]==[1,2,3]
    history=stress_client.get("/api/stress-test/history/fishing",params={"start_year":2018,"end_year":2024}).json()
    assert history["points"] and history["latest_dependency_pct"] is not None
    assert all(point["nominal_growth_contribution_pct"] is None or isinstance(point["nominal_growth_contribution_pct"],float) for point in history["points"])
    concentration=stress_client.get("/api/stress-test/concentration",params={"year":2024}).json()
    expected=sum((item["share_of_activity_gdp_pct"]/100)**2 for item in concentration["included_sectors"])
    assert concentration["hhi"]==pytest.approx(expected)
    assert len(stress_client.get("/api/stress-test/presets").json())==5
