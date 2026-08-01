from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REAL_DATA_RAW_DIR = REPO_ROOT / "data" / "raw"


@pytest.fixture(scope="session")
def real_data_raw_dir() -> Path:
    return REAL_DATA_RAW_DIR


@pytest.fixture()
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path/'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session, tmp_path, monkeypatch):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    from app.config import Settings
    import app.routers.data as data_module

    test_settings = Settings(
        database_url="sqlite:///:memory:",
        upload_dir=str(tmp_path / "uploads"),
        data_raw_dir=str(REAL_DATA_RAW_DIR),
        data_processed_dir=str(tmp_path / "processed"),
    )
    monkeypatch.setattr(data_module, "get_settings", lambda: test_settings)

    from fastapi.testclient import TestClient

    # Deliberately not using TestClient as a context manager: that would run
    # the app's startup event against the real default database instead of
    # the per-test in-memory session overridden above. Routers only need
    # `get_db`, which is already overridden.
    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
