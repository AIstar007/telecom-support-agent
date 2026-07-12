"""
Shared fixtures. The key one is `ingested_test_db`, which builds a real,
isolated ChromaDB instance from the actual policy docs in data/policies/
for each test session — so retrieval tests exercise the real embedding +
retrieval path, not a mock, without polluting the dev chroma_db/ directory.
"""
import os
import shutil

import pytest


@pytest.fixture(scope="session", autouse=True)
def ingested_test_db(tmp_path_factory):
    test_chroma_path = str(tmp_path_factory.mktemp("chroma_test_db"))
    os.environ["CHROMA_PATH"] = test_chroma_path

    # Reset retriever module-level cache so it picks up the new path
    from app.rag import retriever
    retriever._client = None
    retriever._collection = None

    from app.rag.ingest import ingest
    ingest()

    yield

    shutil.rmtree(test_chroma_path, ignore_errors=True)
