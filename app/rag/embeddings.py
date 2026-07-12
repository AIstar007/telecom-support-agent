"""
Offline, dependency-free embedding function.

Chroma's default embedder needs to download a model from HuggingFace at
first use, which isn't reachable in locked-down network environments (and
won't be reachable from most corporate sandboxes either). This is a real,
working hashing-based bag-of-words embedder: deterministic, no downloads,
no API key — good enough for keyword-overlap retrieval over a policy FAQ
corpus. Swap back to a real sentence-transformer or OpenAI embeddings in
an environment with model/API access for higher retrieval quality.
"""
import hashlib
import math
import re
from collections import Counter

DIM = 256


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _hash_index(token: str) -> int:
    return int(hashlib.md5(token.encode()).hexdigest(), 16) % DIM


def embed_one(text: str) -> list[float]:
    tokens = _tokenize(text)
    if not tokens:
        return [0.0] * DIM
    counts = Counter(tokens)
    vec = [0.0] * DIM
    for token, count in counts.items():
        vec[_hash_index(token)] += count
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class HashingEmbeddingFunction:
    """Conforms to Chroma's EmbeddingFunction interface: __call__(list[str]) -> list[list[float]]"""

    # Chroma calls ef.is_legacy() (a method, not an attribute) when
    # serializing collection config. Declaring it True tells Chroma to skip
    # the get_config()/name() registration path we don't implement, which
    # otherwise raises a DeprecationWarning on every collection creation.
    def is_legacy(self) -> bool:
        return True

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [embed_one(t) for t in input]

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self.__call__(input)

    def name(self) -> str:
        return "hashing-bow-256"
