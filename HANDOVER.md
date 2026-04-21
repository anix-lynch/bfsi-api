# HANDOVER — BFSI Sandbox

## Status (2026-04-21)

Phase 1 + Phase 2 complete. Smoke test passes end-to-end.

- Data: 500 customers / 2000 transactions / 100 tickets / 50 loans +
  memos + covenants / 100 wealth clients + 200 advisor notes + 50 KYC
  flags / 300 claims + 100 narratives + 50 fraud indicators / 20
  regulatory docs + 100 internal policies.
- API: `/customers/{id}`, `/tickets/search`, `/loans/{id}`,
  `/advisors/{id}/notes`, `/wealth/{id}`, `/claims/{id}`,
  `/compliance/search`, `/rag/ingest`, `/rag/query`.
- RAG: ChromaDB persistent client, 155-doc corpus (credit memos + reg
  docs + claim narratives).
- Scenario briefs: all 7 written.

## Published

- GitHub: `https://github.com/anix-lynch/bfsi-api` (public)
- Local (Mac Mini): `~/dev/bfsi/`
- Local (Intel): appears via Syncthing on ~/dev/ sync. A fresh venv is
  required on Intel because the Mac Mini venv is arm64:
  `python -m venv .venv && source .venv/bin/activate && pip install -e .`

## Not yet built (Phase 3 — nice-to-have)

- Cost ledger stub for scenario 07.
- Eval harness (retrieval recall@k on a hand-labeled set for scenario 02).
- Streaming endpoints for long RAG responses.

## How to resume

```bash
cd ~/dev/bfsi
source .venv/bin/activate
python data/generate.py     # only if data missing
python -m uvicorn api.main:app --reload
```

Open http://localhost:8000/docs, pick any scenario brief, start building.
