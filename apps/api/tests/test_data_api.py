import pytest


def _require_real_files(real_data_raw_dir):
    for name in ("comptes_nationaux_4.9.1.xlsx", "comptes_nationaux_4.9.2.xlsx"):
        if not (real_data_raw_dir / name).exists():
            pytest.skip(f"Real data file not present: {name}")


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_status_before_import_shows_not_imported(client):
    resp = client.get("/api/data/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["imported"] is False
    assert body["datasets"] == []


def test_full_import_then_status_quality_reconciliation_datasets(client, real_data_raw_dir):
    _require_real_files(real_data_raw_dir)

    import_resp = client.post("/api/data/import")
    assert import_resp.status_code == 200
    report = import_resp.json()
    assert len(report["datasets"]) == 2

    status_resp = client.get("/api/data/status")
    status = status_resp.json()
    assert status["imported"] is True
    assert status["indicator_count"] == 39
    assert status["total_observations"] == 39 * 27

    quality_resp = client.get("/api/data/quality")
    quality = {q["dataset_code"]: q for q in quality_resp.json()}
    assert quality["gdp_by_expenditure"]["total_values"] == 12 * 27
    assert quality["gdp_by_activity"]["total_values"] == 27 * 27
    assert quality["gdp_by_expenditure"]["missing_count"] > 0  # net_acquisition_valuables NA years

    reconciliation_resp = client.get("/api/data/reconciliation")
    reconciliation = reconciliation_resp.json()
    by_year = {r["year"]: r for r in reconciliation}
    assert by_year[2018]["absolute_difference"] == pytest.approx(4317.58, abs=0.01)
    assert by_year[2024]["severity"] == "green"

    datasets_resp = client.get("/api/datasets")
    codes = {d["code"] for d in datasets_resp.json()}
    assert codes == {"gdp_by_expenditure", "gdp_by_activity"}

    one_dataset_resp = client.get("/api/datasets/gdp_by_activity")
    assert one_dataset_resp.status_code == 200
    assert one_dataset_resp.json()["table_number"] == "4.9.2"


def test_dataset_not_found(client):
    resp = client.get("/api/datasets/does_not_exist")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "dataset_not_found"
