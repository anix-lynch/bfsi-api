# Scenario 05 — Grounded Compliance Q&A

## Business pain point
Compliance officers at regulated institutions read upwards of 40 hours of
regulatory guidance and internal policy per week to stay current. They need a
Q&A system that answers policy questions with inline citations to the source
document — hallucinated answers in a compliance context are worse than no
answer at all.

## What to build
A grounded QA system over the regulatory doc + internal policy corpus:

- `POST /rag/ingest?corpus=reg` — index the supervisory letters and bulletins.
- `GET /compliance/search?q=...` — keyword search for sanity checks.
- `POST /rag/query?q=...&k=5` — retrieval with source metadata.

Wire generation on top with strict citation enforcement: every claim in the
answer must map to a retrieved chunk, and the chunk must be quoted (or at
least referenced by title and ID).

## Success criteria
- 100% of answer claims map to a retrieved chunk.
- "I don't know" is a valid answer when retrieval returns nothing relevant.
- An out-of-scope question (e.g., "what's the weather in Tokyo?") gets a
  refusal, not a made-up policy citation.

## Tradeoffs to discuss
- **Extract-then-generate vs. freeform.** Extracting exact citations from
  retrieved chunks before generating reduces hallucination risk but limits
  rephrasing.
- **Retrieval scope.** Indexing every internal policy bloats the index and
  hurts precision; too narrow a scope misses obscure answers. Metadata
  filters (by policy area, by issue date) help.
- **Staleness.** Regs change. A doc-level "last reviewed" date should gate
  confidence in older answers; stale docs should flag themselves.

## What I'd do with more time
_Fill this in after building._
