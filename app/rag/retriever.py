"""
Retrieval wrapper — thin layer over ChromaDB so agents never touch the
vector store directly. Returns text + source metadata for citation.

Fails soft: if the vector store is unreachable, corrupted, or empty, this
returns [] rather than raising — callers (domain agents) already treat an
empty result as "low confidence" and route to escalation, so a retrieval
outage degrades to "ask a human" instead of crashing the request.
"""
import logging
import os

import chromadb

from app.rag.embeddings import HashingEmbeddingFunction

logger = logging.getLogger("copilot.retriever")

COLLECTION_NAME = "telecom_policies"


def get_chroma_path() -> str:
    return os.environ.get("CHROMA_PATH", "./chroma_db")

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=get_chroma_path())
        embed_fn = HashingEmbeddingFunction()
        _collection = _client.get_or_create_collection(COLLECTION_NAME, embedding_function=embed_fn)
    return _collection


def retrieve(query: str, k: int = 3) -> list[dict]:
    if not query or not query.strip():
        return []

    try:
        collection = _get_collection()
        if collection.count() == 0:
            logger.warning("Retrieval requested but collection is empty — has ingest.py been run?")
            return []

        results = collection.query(query_texts=[query], n_results=min(k, collection.count()))
    except Exception:
        logger.exception("Retrieval failed for query: %r", query)
        return []  # fail soft — caller treats this as low confidence, not a crash

    out = []
    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    for text, meta in zip(documents[0], metadatas[0]):
        out.append({"text": text, "source": (meta or {}).get("source", "unknown")})
    return out
