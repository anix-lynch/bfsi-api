"""Smoke test — verifies data generation + API routes without running a server.

Run:  python tests/smoke_test.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402

DB = ROOT / "data" / "bfsi.db"


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] database missing — run `python data/generate.py` first ({DB})")
        return 1

    conn = sqlite3.connect(DB)
    counts = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in (
            "customers", "transactions", "tickets",
            "loans", "credit_memos", "covenants",
            "wealth_clients", "advisors", "advisor_notes", "kyc_flags",
            "claims", "claim_narratives", "fraud_indicators",
            "reg_docs", "policies",
        )
    }
    conn.close()

    for table, n in counts.items():
        status = "OK" if n > 0 else "EMPTY"
        print(f"  [{status}] {table}: {n}")
    if any(v == 0 for v in counts.values()):
        return 1

    client = TestClient(app)
    checks = [
        ("GET", "/health"),
        ("GET", "/customers/1"),
        ("GET", "/tickets/search?q=wire"),
        ("GET", "/loans/1"),
        ("GET", "/advisors/1/notes"),
        ("GET", "/wealth/1"),
        ("GET", "/claims/1"),
        ("GET", "/compliance/search?q=risk"),
    ]
    for method, path in checks:
        r = client.request(method, path)
        ok = 200 <= r.status_code < 300
        print(f"  [{'OK' if ok else 'FAIL'}] {method} {path} -> {r.status_code}")
        if not ok:
            print(f"    body: {r.text[:200]}")
            return 1

    print("\nall smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
