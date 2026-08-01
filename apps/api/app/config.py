"""Application configuration, loaded from environment variables / .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = API_DIR.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Mauritania Economic Intelligence Platform API"
    environment: str = "development"

    database_url: str = f"sqlite:///{(API_DIR / 'var' / 'meip.db').as_posix()}"

    frontend_url: str = "http://localhost:5173"

    upload_dir: str = str(API_DIR / "var" / "uploads")
    max_upload_mb: int = 20

    data_raw_dir: str = str(REPO_ROOT / "data" / "raw")
    data_processed_dir: str = str(REPO_ROOT / "data" / "processed")

    min_forecast_observations: int = 8
    limited_data_warning_threshold: int = 15

    @property
    def cors_origin_list(self) -> list[str]:
        """Allowed browser origins from FRONTEND_URL (comma-separated)."""
        return [origin.strip().rstrip("/") for origin in self.frontend_url.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
