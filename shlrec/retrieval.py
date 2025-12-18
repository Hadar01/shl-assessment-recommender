from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from .utils import normalize_whitespace


@dataclass
class LoadedIndex:
    meta: List[Dict[str, Any]]
    bm25: BM25Okapi
    embeddings: np.ndarray
    embedder: SentenceTransformer


def load_index(index_dir: str | Path, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2") -> LoadedIndex:
    index_dir = Path(index_dir)
    meta = json.loads((index_dir / "meta.json").read_text(encoding="utf-8"))
    with open(index_dir / "bm25.pkl", "rb") as f:
        bm25 = pickle.load(f)
    embeddings = np.load(index_dir / "embeddings.npy")
    embedder = SentenceTransformer(embedding_model)
    return LoadedIndex(meta=meta, bm25=bm25, embeddings=embeddings, embedder=embedder)


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    return [t for t in normalize_whitespace(text).split(" ") if t]


def hybrid_retrieve(
    idx: LoadedIndex,
    query: str,
    alpha: float = 0.35,
    top_n: int = 80,
) -> List[Tuple[int, float]]:
    """Return list[(doc_idx, score)] sorted desc."""
    # BM25
    qtok = _tokenize(query)
    bm = np.array(idx.bm25.get_scores(qtok), dtype=np.float32)
    if bm.max() > 0:
        bm = bm / (bm.max() + 1e-6)

    # Embedding cosine similarity (embeddings are normalized)
    qemb = idx.embedder.encode([query], normalize_embeddings=True)[0].astype(np.float32)
    cos = idx.embeddings @ qemb
    # normalize to 0..1
    cosn = (cos - cos.min()) / (cos.max() - cos.min() + 1e-6)

    score = alpha * bm + (1 - alpha) * cosn
    top_idx = np.argsort(-score)[:top_n]
    return [(int(i), float(score[i])) for i in top_idx]
