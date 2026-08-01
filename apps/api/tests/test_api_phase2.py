import pytest


def _require_real_files(real_data_raw_dir):
    for name in ("comptes_nationaux_4.9.1.xlsx", "comptes_nationaux_4.9.2.xlsx"):
        if not (real_data_raw_dir / name).exists():
            pytest.skip(f"Real data file not present: {name}")


@pytest.fixture()
def imported_client(client, real_data_raw_dir):
    _require_real_files(real_data_raw_dir)
    resp = client.post("/api/data/import")
    assert resp.status_code == 200
    return client


def test_indicators_list_and_series(imported_client):
    resp = imported_client.get("/api/indicators")
    assert resp.status_code == 200
    codes = {i["code"] for i in resp.json()}
    assert "primary_sector" in codes
    assert len(resp.json()) == 39

    series_resp = imported_client.get("/api/indicators/gdp_activity_market_prices/series")
    points = {p["year"]: p["value"] for p in series_resp.json()["points"]}
    assert points[2024] == pytest.approx(429701.30)

    summary_resp = imported_client.get("/api/indicators/gdp_activity_market_prices/summary")
    assert summary_resp.json()["latest_value"] == pytest.approx(429701.30)


def test_indicator_not_found(imported_client):
    resp = imported_client.get("/api/indicators/does_not_exist")
    assert resp.status_code == 404


def test_dashboard_overview_real_values(imported_client):
    resp = imported_client.get("/api/dashboard/overview")
    body = resp.json()
    assert body["latest_year"] == 2024
    assert body["latest_gdp_activity"] == pytest.approx(429701.30)
    assert body["latest_gdp_expenditure"] == pytest.approx(429701.30)
    assert body["latest_trade_balance"] == pytest.approx(-56920.50)
    assert body["largest_sector_code"] == "tertiary_sector"


def test_dashboard_year_snapshot(imported_client):
    resp = imported_client.get("/api/dashboard/year/2018")
    body = resp.json()
    assert body["gdp_activity"] == pytest.approx(266637.60)
    assert body["gdp_expenditure"] == pytest.approx(262320.02)
    assert body["reconciliation_absolute_difference"] == pytest.approx(4317.58, abs=0.01)


def test_dashboard_year_not_available(imported_client):
    resp = imported_client.get("/api/dashboard/year/1900")
    assert resp.status_code == 404


def test_activity_sectors_and_detail(imported_client):
    resp = imported_client.get("/api/activity/sectors")
    codes = {s["code"] for s in resp.json()}
    assert codes == {"primary_sector", "secondary_sector", "tertiary_sector"}

    detail_resp = imported_client.get("/api/activity/sectors/primary_sector")
    detail = detail_resp.json()
    values_2024 = next(p["value"] for p in detail["series"] if p["year"] == 2024)
    assert values_2024 == pytest.approx(83568.90)
    assert detail["cagr_pct"] is not None
    assert detail["completeness_score_pct"] == pytest.approx(100.0)
    assert detail["source"] == "ANSADE/CN"


def test_activity_sectors_support_selected_year(imported_client):
    resp = imported_client.get("/api/activity/sectors", params={"year": 2018})
    assert resp.status_code == 200
    primary = next(item for item in resp.json() if item["code"] == "primary_sector")
    assert primary["year"] == 2018
    assert primary["latest_value"] == pytest.approx(63075.70)
    assert imported_client.get("/api/activity/sectors", params={"year": 1900}).status_code == 400


def test_activity_mining(imported_client):
    resp = imported_client.get("/api/activity/mining")
    body = resp.json()
    assert body["year"] == 2024
    branch_values = {b["code"]: b["latest_value"] for b in body["branches"]}
    assert branch_values["snim_iron"] == pytest.approx(27226.00)
    assert branch_values["gold_copper"] == pytest.approx(43711.70)
    assert body["snim_share_of_metallic_pct"] == pytest.approx(27226.0 / 70937.7 * 100)
    assert body["gold_copper_share_of_metallic_pct"] == pytest.approx(43711.7 / 70937.7 * 100)


def test_expenditure_trade(imported_client):
    resp = imported_client.get("/api/expenditure/trade")
    body = resp.json()
    balance_2024 = next(p["value"] for p in body["trade_balance_series"] if p["year"] == 2024)
    assert balance_2024 == pytest.approx(-56920.50)
    assert body["maximum_balance_year"] is not None
    assert body["largest_deficit"] <= body["maximum_balance"]
    assert body["exports_growth_series"]


def test_expenditure_overview_and_missing_valuables(imported_client):
    overview = imported_client.get("/api/expenditure/overview").json()
    assert overview["trade_balance"] == pytest.approx(-56920.50)
    assert overview["trade_openness_pct"] == pytest.approx((169986.60 + 226907.10) / 429701.30 * 100)
    investment = imported_client.get("/api/expenditure/investment").json()
    assert investment["warnings"]
    assert 1998 in investment["missing_years"]


def test_analytics_growth_endpoint(imported_client):
    resp = imported_client.get("/api/analytics/growth", params={"indicator": "gdp_activity_market_prices"})
    body = resp.json()
    point_2024 = next(p for p in body["points"] if p["year"] == 2024)
    assert point_2024["value"] == pytest.approx(429701.30)
    assert point_2024["growth_pct"] is not None


def test_analytics_contribution_endpoint(imported_client):
    resp = imported_client.get(
        "/api/analytics/contribution",
        params={"part": "primary_sector", "whole": "gdp_activity_market_prices"},
    )
    body = resp.json()
    point_2024 = next(p for p in body["points"] if p["year"] == 2024)
    expected_share = 83568.90 / 429701.30 * 100
    assert point_2024["share_pct"] == pytest.approx(expected_share, abs=0.01)


def test_analytics_compare_endpoint(imported_client):
    resp = imported_client.get(
        "/api/analytics/compare", params={"first": "fishing", "second": "extractive_activities"}
    )
    body = resp.json()
    assert body["correlation"] is not None
    assert len(body["common_years"]) == 27


def test_analytics_anomalies_endpoint(imported_client):
    resp = imported_client.get("/api/analytics/anomalies", params={"indicator": "snim_iron"})
    body = resp.json()
    assert "alerts" in body
    for alert in body["alerts"]:
        assert alert["explanation_fr"]
        assert alert["explanation_ar"]


def test_forecast_endpoint_real_gdp(imported_client):
    resp = imported_client.post("/api/forecast", json={"indicator_code": "gdp_activity_market_prices", "horizon_years": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["predicted_values"]) == 3
    assert body["reliability"] in ("low", "moderate", "high")
    assert body["disclaimer_fr"]
    assert body["disclaimer_ar"]


def test_forecast_new_request_shape_period_and_validation(imported_client):
    resp = imported_client.post("/api/forecast", json={"indicator_code": "gdp_activity_market_prices", "horizon": 2, "start_year": 2010, "preferred_model": "naive_last_value"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["predicted_values"]) == 2
    assert body["historical_start_year"] == 2010
    assert body["model_name"] == "naive_last_value"
    assert imported_client.post("/api/forecast", json={"indicator_code": "gdp_activity_market_prices", "horizon": 4}).status_code == 422
    assert imported_client.post("/api/forecast", json={"indicator_code": "gdp_activity_market_prices", "start_year": 2020, "end_year": 2010}).status_code == 422


def test_forecast_endpoint_insufficient_data(client, db_session):
    # Indicator taxonomy seeded, but no values imported: 0 observations.
    from app.ingestion.seed import seed_indicators

    seed_indicators(db_session)

    resp = client.post("/api/forecast", json={"indicator_code": "gdp_activity_market_prices"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "insufficient_observations"
