# Scenario 02 — Credit Memo RAG for Underwriters

## Business pain point
Commercial underwriters spend roughly three weeks on diligence per mid-market
loan. A meaningful slice of that is searching prior credit memos, covenant
notes, and industry write-ups for precedent. Leadership wants underwriters to
get a grounded answer to "have we underwritten something like this before, and
what were the terms?" in under a minute.

## What to build
A retrieval-augmented QA system over the credit memo corpus (and covenant
notes). Endpoints to use:

- `POST /rag/ingest?corpus=credit_memo` — build the index.
- `POST /rag/query?q=...&k=5` — retrieve top-k chunks with source metadata.
- `GET /loans/{id}` — join retrieved memos back to their structured loan record.

Wire an LLM of your choice on top to generate the final answer. Every answer
must cite the specific loan ID(s) it pulled from.

## Success criteria
- Retrieval recall@5 above 0.8 on a small labeled eval set you construct.
- Every cited loan ID exists in the database (no hallucinated IDs).
- Answer quality survives a "what if the borrower has no prior relationship"
  question (retrieval returns nothing relevant — model should say so).

## Tradeoffs to discuss
- **Chunk size.** Short chunks give cleaner citations; long chunks preserve
  narrative flow. Credit memos reward long chunks.
- **Hybrid vs. dense retrieval.** BM25 catches loan numbers and industry
  terms; dense retrieval catches semantic paraphrase. A hybrid score often
  wins on this kind of corpus.
- **Structured filter pre-step.** Before retrieval, filter by industry or
  loan size to avoid irrelevant matches — a common production pattern.

## What I'd do with more time
_Fill this in after building._
