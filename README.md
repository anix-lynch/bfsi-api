# BFSI Sandbox

A local, synthetic-data playground for prototyping RAG and agent systems
against realistic **Banking, Financial Services, and Insurance** workloads.

Five domains in one SQLite database, a FastAPI layer exposing them as
HTTP endpoints, a ChromaDB-backed retrieval module, and seven scenario
briefs that map each endpoint to a concrete enterprise use case.

No real data, no cloud dependencies, no Docker. Runs on a laptop.

## Quickstart

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Generate synthetic data (deterministic; Faker seed 42)
python data/generate.py

# 3. Start the API
python -m uvicorn api.main:app --reload

# 4. Open docs
open http://localhost:8000/docs
```

## Smoke test

```bash
python tests/smoke_test.py
```

Verifies every table is populated and every REST endpoint returns 2xx.

## What's in the box

| Domain | Records | Endpoint |
|---|---|---|
| Retail banking — customers, transactions, service tickets | 500 / 2000 / 100 | `/customers/{id}`, `/tickets/search` |
| Commercial lending — loan applications, credit memos, covenants | 50 loans | `/loans/{id}` |
| Wealth management — clients, advisors, meeting notes, KYC flags | 100 / 12 / 200 / 50 | `/wealth/{id}`, `/advisors/{id}/notes` |
| Insurance claims — claims, narratives, fraud indicators | 300 / 100 / 50 | `/claims/{id}` |
| Compliance — regulatory docs, internal policies | 20 / 100 | `/compliance/search` |
| RAG — ingest + retrieval over the unstructured corpora | — | `/rag/ingest`, `/rag/query` |

All PII-shaped columns use a `__synthetic__` prefix to make it explicit
that no real identifiers are stored.

## Scenarios

Seven briefs under [`scenarios/`](scenarios/) — each maps a domain endpoint
to a realistic enterprise pain point with a business framing, success
criteria, and tradeoffs to discuss:

1. [Retail Banking CSR Copilot](scenarios/01_retail_banking_copilot.md)
2. [Credit Memo RAG for Underwriters](scenarios/02_credit_memo_rag.md)
3. [Wealth Advisor Recall](scenarios/03_advisor_recall.md)
4. [Multi-Agent Claims Triage](scenarios/04_claims_triage.md)
5. [Grounded Compliance Q&A](scenarios/05_compliance_qa.md)
6. [Cross-Product Customer 360](scenarios/06_cross_product_360.md)
7. [Tiered Model Routing with Cost Ledger](scenarios/07_cost_routing_demo.md)

## Layout

```
bfsi-api/
├── data/
│   ├── generate.py      # Faker-driven synthetic generator
│   ├── bfsi.db          # SQLite (gitignored)
│   └── docs/            # long-form text export for RAG ingest
├── api/
│   ├── main.py          # FastAPI app + all routes
│   └── rag.py           # Chroma ingest + query
├── scenarios/           # one brief per use case
├── tests/smoke_test.py
└── pyproject.toml
```

## Why synthetic

Every record is fabricated by [Faker](https://faker.readthedocs.io/) with a
fixed seed, so the dataset is deterministic across machines. The point is to
have realistically *shaped* BFSI data — messy free-text narratives, PII-like
fields, multi-table joins, regulator-style prose — without the risk of
touching production data during prototyping.

## License

MIT.
