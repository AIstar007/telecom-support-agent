"""
Ingest policy documents into ChromaDB.

Run: python -m app.rag.ingest
Expects markdown/txt files under data/policies/*.md
"""
import glob
import os
import re

import chromadb

from app.rag.embeddings import HashingEmbeddingFunction

COLLECTION_NAME = "telecom_policies"


def get_chroma_path() -> str:
    """Read lazily, not bound at import time — a module-level constant here
    would freeze whatever CHROMA_PATH was set (or unset) at first import,
    which breaks test isolation (fixtures that set the env var *after*
    another module already imported this one would be silently ignored)."""
    return os.environ.get("CHROMA_PATH", "./chroma_db")


def chunk_text(text: str, max_chunk_size: int = 800) -> list[str]:
    """
    Split on markdown ## section boundaries first, then fall back to a
    fixed-size window only for sections that exceed max_chunk_size.

    Fixed-size character windows (the original approach) cut straight
    through section boundaries, producing chunks that blend two unrelated
    topics together — e.g. the tail of a "Slow data speeds" troubleshooting
    section merged with the next section, diluting the chunk's relevance to
    either topic and confusing retrieval. Splitting on structure first keeps
    each chunk topically coherent, which is what retrieval quality actually
    depends on here, not raw chunk size.
    """
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    chunks = []
    for section in sections:
        if len(section) <= max_chunk_size:
            chunks.append(section)
        else:
            start = 0
            while start < len(section):
                chunks.append(section[start:start + max_chunk_size])
                start += max_chunk_size
    return chunks


def ingest():
    client = chromadb.PersistentClient(path=get_chroma_path())
    embed_fn = HashingEmbeddingFunction()
    collection = client.get_or_create_collection(COLLECTION_NAME, embedding_function=embed_fn)

    doc_id = 0
    for path in glob.glob("data/policies/*.md"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        for chunk in chunk_text(text):
            collection.add(
                ids=[f"doc-{doc_id}"],
                documents=[chunk],
                metadatas=[{"source": os.path.basename(path)}],
            )
            doc_id += 1

    print(f"Ingested {doc_id} chunks into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest()
