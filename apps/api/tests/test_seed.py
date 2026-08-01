from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion.seed import seed_indicators
from app.ingestion.taxonomy import all_rows
from app.models.indicator import Indicator


def _session(tmp_path, name):
    engine = create_engine(f"sqlite:///{tmp_path/name}")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_seed_creates_all_taxonomy_rows(tmp_path):
    db = _session(tmp_path, "seed1.db")
    created = seed_indicators(db)
    assert created == len(all_rows()) == 39
    assert db.query(Indicator).count() == 39


def test_seed_is_idempotent(tmp_path):
    db = _session(tmp_path, "seed2.db")
    seed_indicators(db)
    assert seed_indicators(db) == 0


def test_seed_wires_activity_hierarchy(tmp_path):
    db = _session(tmp_path, "seed3.db")
    seed_indicators(db)

    primary = db.query(Indicator).filter(Indicator.code == "primary_sector").first()
    alias = db.query(Indicator).filter(Indicator.code == "agriculture_fishing_forestry").first()
    fishing = db.query(Indicator).filter(Indicator.code == "fishing").first()
    snim = db.query(Indicator).filter(Indicator.code == "snim_iron").first()
    metallic = db.query(Indicator).filter(Indicator.code == "metallic_mineral_extraction").first()

    assert alias.parent_indicator_id == primary.id
    assert alias.is_alias is True
    assert alias.alias_of_indicator_id == primary.id
    assert fishing.parent_indicator_id == alias.id
    assert snim.parent_indicator_id == metallic.id
    assert snim.hierarchy_level == 5


def test_seed_marks_aggregates_and_source_side(tmp_path):
    db = _session(tmp_path, "seed4.db")
    seed_indicators(db)

    gdp_expenditure = db.query(Indicator).filter(Indicator.code == "gdp_expenditure").first()
    gdp_activity = db.query(Indicator).filter(Indicator.code == "gdp_activity_market_prices").first()

    assert gdp_expenditure.is_aggregate is True
    assert gdp_expenditure.source_side == "expenditure"
    assert gdp_activity.is_aggregate is True
    assert gdp_activity.source_side == "activity"
