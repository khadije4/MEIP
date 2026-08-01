"""Integration tests for the full idempotent import pipeline against the
real data files, including the GDP reconciliation it computes."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion.service import import_all
from app.models.economic_value import EconomicValue
from app.models.indicator import Indicator
from app.models.reconciliation import ReconciliationIssue


@pytest.fixture()
def db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path/'import_test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _require_real_files(real_data_raw_dir):
    for name in ("comptes_nationaux_4.9.1.xlsx", "comptes_nationaux_4.9.2.xlsx"):
        if not (real_data_raw_dir / name).exists():
            pytest.skip(f"Real data file not present: {name}")


def test_import_all_persists_exact_values(db, real_data_raw_dir, tmp_path):
    _require_real_files(real_data_raw_dir)
    processed_dir = tmp_path / "processed"

    report = import_all(db, real_data_raw_dir, processed_dir)

    assert report["indicators_seeded_new"] == 39
    assert len(report["datasets"]) == 2
    for ds in report["datasets"]:
        assert ds["label_mismatches"] == []
        assert ds["warnings"] == []

    gdp_activity = db.query(Indicator).filter(Indicator.code == "gdp_activity_market_prices").first()
    value_2024 = (
        db.query(EconomicValue)
        .filter(EconomicValue.indicator_id == gdp_activity.id, EconomicValue.year == 2024)
        .first()
    )
    assert value_2024.value == pytest.approx(429701.30)
    assert value_2024.quality_flag == "ok"

    net_acq = db.query(Indicator).filter(Indicator.code == "net_acquisition_valuables").first()
    value_1998 = (
        db.query(EconomicValue)
        .filter(EconomicValue.indicator_id == net_acq.id, EconomicValue.year == 1998)
        .first()
    )
    assert value_1998.is_missing is True
    assert value_1998.value is None

    assert (processed_dir / "gdp_by_activity.csv").exists()
    assert (processed_dir / "gdp_by_expenditure.csv").exists()
    assert (processed_dir / "validation_report.json").exists()


def test_import_all_is_idempotent(db, real_data_raw_dir, tmp_path):
    _require_real_files(real_data_raw_dir)
    processed_dir = tmp_path / "processed"

    import_all(db, real_data_raw_dir, processed_dir)
    count_after_first = db.query(EconomicValue).count()

    import_all(db, real_data_raw_dir, processed_dir)
    count_after_second = db.query(EconomicValue).count()

    assert count_after_first == count_after_second
    assert count_after_first == (12 + 27) * 27  # 39 indicators x 27 years


def test_reconciliation_rows_reflect_2018_2019_2020_divergence_and_2024_agreement(db, real_data_raw_dir, tmp_path):
    _require_real_files(real_data_raw_dir)
    import_all(db, real_data_raw_dir, tmp_path / "processed")

    issues_by_year = {i.year: i for i in db.query(ReconciliationIssue).all()}

    assert issues_by_year[2018].absolute_difference == pytest.approx(4317.58, abs=0.01)
    assert issues_by_year[2018].severity in ("orange", "red", "yellow")

    assert issues_by_year[2024].absolute_difference == pytest.approx(0.0, abs=0.01)
    assert issues_by_year[2024].severity == "green"
