FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Ingest policy docs into the vector store at container start, not build
# time — keeps the image reusable if docs change without a rebuild, and
# fails loudly here rather than silently degrading to empty retrieval.
CMD python -m app.rag.ingest && uvicorn app.main:app --host 0.0.0.0 --port 8000
