"""One-off DB initialization + indicator taxonomy seed, for use outside the
FastAPI startup event (e.g. CI, first-time setup scripts).

Usage (from apps/api, with the venv activated):
    python ../../scripts/init_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from app.database import SessionLocal, init_db  # noqa: E402
from app.ingestion.seed import seed_indicators  # noqa: E402


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        created = seed_indicators(db)
        print(f"Database initialized. Indicator taxonomy seeded ({created} new rows).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
