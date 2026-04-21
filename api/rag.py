"""Local ChromaDB-backed retrieval layer.

Chunks text files from data/docs/ and stores them in a persistent Chroma
collection. Query returns the top-k chunks plus their source filenames.

This module intentionally ships without LLM generation wired up — the
/rag/query endpoint returns retrieved context so callers can plug in
whatever generator they prefer (Claude, Gemini, local models, etc.).
"""
from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma"
COLLECTION = "bfsi_corpus"


def _client() -> chromadb.PersistentClient:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))


def _chunks(text: str, size: int = 600, overlap: int = 80) -> list[str]:
    if len(text) <= size:
        return [text]
    out: list[str] = []
    i = 0
    while i < len(text):
        out.append(text[i : i + size])
        i += size - overlap
    return out


def ingest(corpus: str = "all") -> int:
    """Read files from data/docs/, chunk, and upsert into Chroma.

    corpus: "all" | "credit_memo" | "reg" | "claim"
    Returns the number of chunks indexed.
    """
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Docs dir missing: {DOCS_DIR}. Run data/generate.py first.")

    prefix_map = {
        "credit_memo": "credit_memo_",
        "reg": "reg_",
        "claim": "claim_",
    }
    if corpus == "all":
        paths = sorted(DOCS_DIR.glob("*.txt"))
    else:
        prefix = prefix_map.get(corpus)
        if prefix is None:
            raise ValueError(f"Unknown corpus '{corpus}'. Use all|credit_memo|reg|claim.")
        paths = sorted(DOCS_DIR.glob(f"{prefix}*.txt"))

    client = _client()
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    coll = client.create_collection(COLLECTION)

    ids, docs, metas = [], [], []
    for p in paths:
        text = p.read_text()
        for idx, ch in enumerate(_chunks(text)):
            ids.append(f"{p.stem}__{idx}")
            docs.append(ch)
            metas.append({"source": p.name, "chunk": idx})

    if docs:
        coll.add(ids=ids, documents=docs, metadatas=metas)
    return len(docs)


def query(q: str, k: int = 5) -> dict:
    coll = _client().get_or_create_collection(COLLECTION)
    res = coll.query(query_texts=[q], n_results=k)
    hits = []
    for doc, meta, dist in zip(
        res.get("documents", [[]])[0],
        res.get("metadatas", [[]])[0],
        res.get("distances", [[]])[0],
    ):
        hits.append({"source": meta.get("source"), "chunk": meta.get("chunk"), "distance": dist, "text": doc})
    return {"query": q, "k": k, "hits": hits}
