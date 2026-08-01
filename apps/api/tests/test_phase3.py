import pytest


@pytest.fixture()
def phase3_client(client, real_data_raw_dir):
    for name in ("comptes_nationaux_4.9.1.xlsx", "comptes_nationaux_4.9.2.xlsx"):
        if not (real_data_raw_dir / name).exists(): pytest.skip("Real workbooks are required")
    assert client.post("/api/data/import").status_code == 200
    return client


def test_french_assistant_supported_examples_use_database_values(phase3_client):
    cases = [
        ("Quel était le PIB en 2024 ?", "indicator_value"),
        ("Quelle est la différence entre les deux séries du PIB en 2018 ?", "gdp_reconciliation"),
        ("Quel était le plus grand secteur en 2024 ?", "largest_sector"),
        ("Comparez la pêche et les activités extractives.", "compare"),
        ("Comment l’or et le cuivre ont-ils évolué ?", "evolution"),
        ("Quel était le solde commercial en 2024 ?", "trade_balance"),
        ("Quel était le taux d’investissement en 2022 ?", "investment_rate"),
        ("En quelle année la pêche a-t-elle le plus baissé ?", "largest_decrease"),
        ("Quelles branches sont les plus volatiles ?", "volatility_ranking"),
        ("Donnez une prévision expérimentale du PIB.", "forecast"),
    ]
    for question, intent in cases:
        response = phase3_client.post("/api/assistant/query", json={"question": question})
        assert response.status_code == 200, response.text
        body = response.json(); assert body["language"] == "fr"; assert body["intent"] == intent
        assert body["supported"] is True; assert body["values_used"]
        assert all(v["source_file"].endswith(".xlsx") and v["unit"] == "Millions de MRU" for v in body["values_used"])


def test_arabic_assistant_and_exact_trade_balance(phase3_client):
    response = phase3_client.post("/api/assistant/query", json={"question": "ما الميزان التجاري سنة 2024؟"})
    assert response.status_code == 200
    body = response.json(); assert body["language"] == "ar"; assert body["intent"] == "trade_balance"
    values = {v["indicator_code"]: v["value"] for v in body["values_used"]}
    assert values["exports"] == pytest.approx(169986.60); assert values["imports"] == pytest.approx(226907.10)
    assert "-56,920.50" in body["answer"]


def test_arabic_assistant_supported_examples(phase3_client):
    cases = [
        ("ما قيمة الناتج المحلي سنة 2024؟", "indicator_value"),
        ("ما الفرق بين الناتج حسب الأنشطة والناتج حسب الإنفاق سنة 2018؟", "gdp_reconciliation"),
        ("ما أكبر قطاع في سنة 2024؟", "largest_sector"),
        ("قارن بين الصيد والاستخراج.", "compare"),
        ("كيف تطور قطاع الذهب والنحاس؟", "evolution"),
        ("ما معدل الاستثمار سنة 2022؟", "investment_rate"),
        ("ما السنة التي شهدت أكبر انخفاض في الصيد؟", "largest_decrease"),
        ("ما القطاعات الأكثر تقلباً؟", "volatility_ranking"),
        ("أعطني توقع الناتج المحلي للسنوات القادمة.", "forecast"),
    ]
    for question, intent in cases:
        body = phase3_client.post("/api/assistant/query", json={"question":question}).json()
        assert body["language"] == "ar"; assert body["intent"] == intent; assert body["supported"] is True
        assert body["values_used"]


def test_assistant_refuses_unsupported_information(phase3_client):
    body = phase3_client.post("/api/assistant/query", json={"question": "Quel est le taux de chômage ?"}).json()
    assert body["supported"] is False; assert body["values_used"] == []


def test_french_pdf_arabic_pdf_and_csv_reports(phase3_client):
    for language in ("fr", "ar"):
        response = phase3_client.post("/api/reports/generate", json={"indicator_code":"gdp_activity_market_prices", "start_year":2018, "end_year":2024, "language":language, "format":"pdf"})
        assert response.status_code == 200, response.text
        assert response.headers["content-type"].startswith("application/pdf")
        assert response.content.startswith(b"%PDF") and response.content.rstrip().endswith(b"%%EOF")
    csv_response = phase3_client.post("/api/reports/generate", json={"indicator_code":"exports", "start_year":2023, "end_year":2024, "language":"fr", "format":"csv"})
    assert csv_response.status_code == 200; assert b"2024,169986.6" in csv_response.content


def test_report_validation_and_unknown_indicator(phase3_client):
    assert phase3_client.post("/api/reports/generate", json={"indicator_code":"exports", "start_year":2024, "end_year":2020}).status_code == 422
    assert phase3_client.post("/api/reports/generate", json={"indicator_code":"unknown"}).status_code == 404
    assert phase3_client.post("/api/reports/generate", json={"indicator_code":"exports", "start_year":1900, "end_year":1901}).status_code == 400
