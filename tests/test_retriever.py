from app.rag.retriever import retrieve


def test_retrieve_finds_relevant_billing_chunk():
    results = retrieve("why did my bill increase this month", k=3)
    assert len(results) > 0
    sources = [r["source"] for r in results]
    assert "billing_faq.md" in sources


def test_retrieve_finds_relevant_plan_chunk():
    # Note: the hashing bag-of-words embedder (app/rag/embeddings.py) has no
    # IDF weighting, so it relies on literal keyword overlap rather than real
    # semantic similarity — it needs the query to share actual vocabulary
    # with the corpus (plan names, "GB", "cost") rather than purely generic
    # phrasing. This is a documented trade-off of the offline embedder, not
    # a bug; swap in a real embedding model for semantic queries at scale.
    results = retrieve("how much does the Unlimited 5G plan cost", k=3)
    assert len(results) > 0
    sources = [r["source"] for r in results]
    assert "plan_catalog.md" in sources


def test_retrieve_finds_relevant_troubleshooting_chunk():
    results = retrieve("my phone shows no service", k=3)
    assert len(results) > 0
    sources = [r["source"] for r in results]
    assert "troubleshooting_guide.md" in sources


def test_retrieve_returns_text_and_source_for_each_result():
    results = retrieve("data overage charges", k=2)
    for r in results:
        assert "text" in r and isinstance(r["text"], str) and len(r["text"]) > 0
        assert "source" in r and isinstance(r["source"], str)
