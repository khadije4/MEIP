"""Idempotent CLI importer for the two real ANSADE/CN national-accounts
workbooks in data/raw. Re-running this script does not duplicate rows.

Usage (from repo root, with apps/api's venv activated):
    python scripts/import_national_accounts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API_DIR = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from app.config import get_settings  # noqa: E402
from app.database import SessionLocal, init_db  # noqa: E402
from app.ingestion.service import import_all  # noqa: E402


def main() -> None:
    settings = get_settings()
    init_db()
    db = SessionLocal()
    try:
        report = import_all(
            db,
            raw_dir=Path(settings.data_raw_dir),
            processed_dir=Path(settings.data_processed_dir),
        )
    finally:
        db.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\n--- Summary ---")
    print(f"Indicators newly seeded: {report['indicators_seeded_new']}")
    for ds in report["datasets"]:
        print(
            f"[{ds['table_number']}] {ds['code']}: {ds['indicator_count']} indicators, "
            f"{ds['observation_count']} observations, {ds['missing_count']} missing, "
            f"{ds['nonnumeric_count']} nonnumeric, completeness={ds['completeness_pct']}%"
        )
        if ds["label_mismatches"]:
            print(f"  WARNING label mismatches: {ds['label_mismatches']}")
        for w in ds["warnings"]:
            print(f"  WARNING: {w}")
    print(f"Reconciliation rows (GDP expenditure vs. activity): {report['reconciliation_rows']}")


if __name__ == "__main__":
    main()
