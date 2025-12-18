from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from .utils import normalize_whitespace


@dataclass
class IndexArtifacts:
    meta: List[Dict[str, Any]]
    bm25: BM25Okapi
    corpus_tokens: List[List[str]]
    embeddings: np.ndarray


def _tokenize(text: str) -> List[str]:
    # simple word tokenizer
    text = (text or "").lower()
    return [t for t in normalize_whitespace(text).split(" ") if t]


def build_index(
    catalog_jsonl: str | Path,
    index_dir: str | Path,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> None:
    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)

    # Load catalog items
    meta: List[Dict[str, Any]] = []
    with open(catalog_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                meta.append(json.loads(line))

    # Build corpus text
    corpus = []
    for it in meta:
        fields = [
            it.get("name", ""),
            it.get("description", ""),
            " ".join(it.get("test_type", []) or []),
            f"Duration {it.get('duration', '')} minutes",
            f"Remote {it.get('remote_support', '')}",
            f"Adaptive {it.get('adaptive_support', '')}",
        ]
        corpus.append(normalize_whitespace(" . ".join(fields)))

    corpus_tokens = [_tokenize(t) for t in corpus]
    bm25 = BM25Okapi(corpus_tokens)

    # Embeddings
    model = SentenceTransformer(embedding_model)
    embs = model.encode(corpus, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.asarray(embs, dtype=np.float32)

    # Save
    (index_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(index_dir / "bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)
    with open(index_dir / "corpus_tokens.pkl", "wb") as f:
        pickle.dump(corpus_tokens, f)
    np.save(index_dir / "embeddings.npy", embeddings)

