"""FastAPI entrypoint for the BFSI sandbox.

Local serve:  python -m uvicorn api.main:app --reload
Docs:         http://localhost:8000/docs
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query

from api import rag

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "bfsi.db"

app = FastAPI(
    title="BFSI Sandbox API",
    description="Synthetic BFSI data + RAG endpoints for rapid prototyping "
                "against realistic banking, lending, wealth, insurance, and "
                "compliance workloads.",
    version="0.1.0",
)


@contextmanager
def db():
    if not DB_PATH.exists():
        raise HTTPException(503, f"Database not found at {DB_PATH}. Run `python data/generate.py` first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def rows_to_dicts(rows) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "db_present": str(DB_PATH.exists())}


# -------- Retail banking --------

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    with db() as conn:
        cust = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
        if not cust:
            raise HTTPException(404, f"Customer {customer_id} not found")
        txns = conn.execute(
            "SELECT * FROM transactions WHERE customer_id=? ORDER BY txn_date DESC LIMIT 50",
            (customer_id,),
        ).fetchall()
        tix = conn.execute(
            "SELECT id, created_at, channel, subject, status FROM tickets WHERE customer_id=? ORDER BY created_at DESC",
            (customer_id,),
        ).fetchall()
        return {
            "customer": dict(cust),
            "recent_transactions": rows_to_dicts(txns),
            "tickets": rows_to_dicts(tix),
        }


@app.get("/tickets/search")
def search_tickets(q: str = Query(..., min_length=2), limit: int = 20):
    with db() as conn:
        like = f"%{q}%"
        rows = conn.execute(
            "SELECT * FROM tickets WHERE subject LIKE ? OR body LIKE ? ORDER BY created_at DESC LIMIT ?",
            (like, like, limit),
        ).fetchall()
        return {"query": q, "count": len(rows), "results": rows_to_dicts(rows)}


# -------- Commercial lending --------

@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    with db() as conn:
        loan = conn.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
        if not loan:
            raise HTTPException(404, f"Loan {loan_id} not found")
        memo = conn.execute("SELECT * FROM credit_memos WHERE loan_id=?", (loan_id,)).fetchone()
        cov = conn.execute("SELECT * FROM covenants WHERE loan_id=?", (loan_id,)).fetchall()
        return {
            "loan": dict(loan),
            "credit_memo": dict(memo) if memo else None,
            "covenants": rows_to_dicts(cov),
        }


# -------- Wealth management --------

@app.get("/advisors/{advisor_id}/notes")
def advisor_notes(advisor_id: int, limit: int = 20):
    with db() as conn:
        advisor = conn.execute("SELECT * FROM advisors WHERE id=?", (advisor_id,)).fetchone()
        if not advisor:
            raise HTTPException(404, f"Advisor {advisor_id} not found")
        notes = conn.execute(
            "SELECT n.*, c.__synthetic__name AS client_name FROM advisor_notes n "
            "JOIN wealth_clients c ON c.id = n.wealth_client_id "
            "WHERE n.advisor_id=? ORDER BY n.meeting_date DESC LIMIT ?",
            (advisor_id, limit),
        ).fetchall()
        return {"advisor": dict(advisor), "notes": rows_to_dicts(notes)}


@app.get("/wealth/{client_id}")
def wealth_client(client_id: int):
    with db() as conn:
        c = conn.execute("SELECT * FROM wealth_clients WHERE id=?", (client_id,)).fetchone()
        if not c:
            raise HTTPException(404, f"Wealth client {client_id} not found")
        notes = conn.execute(
            "SELECT * FROM advisor_notes WHERE wealth_client_id=? ORDER BY meeting_date DESC",
            (client_id,),
        ).fetchall()
        flags = conn.execute(
            "SELECT * FROM kyc_flags WHERE wealth_client_id=?",
            (client_id,),
        ).fetchall()
        return {
            "client": dict(c),
            "notes": rows_to_dicts(notes),
            "kyc_flags": rows_to_dicts(flags),
        }


# -------- Insurance claims --------

@app.get("/claims/{claim_id}")
def get_claim(claim_id: int):
    with db() as conn:
        claim = conn.execute("SELECT * FROM claims WHERE id=?", (claim_id,)).fetchone()
        if not claim:
            raise HTTPException(404, f"Claim {claim_id} not found")
        narratives = conn.execute(
            "SELECT * FROM claim_narratives WHERE claim_id=?", (claim_id,),
        ).fetchall()
        fraud = conn.execute(
            "SELECT * FROM fraud_indicators WHERE claim_id=?", (claim_id,),
        ).fetchall()
        return {
            "claim": dict(claim),
            "narratives": rows_to_dicts(narratives),
            "fraud_indicators": rows_to_dicts(fraud),
        }


# -------- Compliance / regulatory --------

@app.get("/compliance/search")
def compliance_search(q: str = Query(..., min_length=2), limit: int = 10):
    with db() as conn:
        like = f"%{q}%"
        docs = conn.execute(
            "SELECT id, doc_type, title, issued_date FROM reg_docs "
            "WHERE title LIKE ? OR body LIKE ? ORDER BY issued_date DESC LIMIT ?",
            (like, like, limit),
        ).fetchall()
        policies = conn.execute(
            "SELECT id, policy_area, title FROM policies "
            "WHERE title LIKE ? OR snippet LIKE ? LIMIT ?",
            (like, like, limit),
        ).fetchall()
        return {
            "query": q,
            "reg_docs": rows_to_dicts(docs),
            "policies": rows_to_dicts(policies),
        }


# -------- RAG --------

@app.post("/rag/ingest")
def rag_ingest(corpus: str = Query("all", description="all | credit_memo | reg | claim")):
    count = rag.ingest(corpus)
    return {"corpus": corpus, "chunks_indexed": count}


@app.post("/rag/query")
def rag_query(q: str = Query(..., min_length=3), k: int = 5):
    return rag.query(q, k=k)
