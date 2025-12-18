"""
Two-stage retrieval: fast BM25 filtering + semantic reranking.
Improves both speed and quality.
"""
from __future__ import annotations

from typing import List, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


def two_stage_retrieve(
    bm25: BM25Okapi,
    embeddings: np.ndarray,
    embedder: SentenceTransformer,
    query: str,
    alpha: float = 0.40,
    top_n: int = 60,
    bm25_cutoff: float = 0.0,  # Filter low BM25 scores
) -> List[Tuple[int, float]]:
    """
    Two-stage retrieval:
    1. Stage 1: Fast BM25 filtering (retrieve top_n * 2)
    2. Stage 2: Semantic reranking (hybrid score)
    
    This improves both speed and quality by:
    - Using BM25 for fast exact-match filtering
    - Using semantic search to find similar concepts
    - Blending scores with optimized weights
    """
    # Stage 1: BM25 filtering
    query_tokens = query.lower().split()
    bm25_scores = np.array(bm25.get_scores(query_tokens), dtype=np.float32)
    
    # Normalize BM25 scores
    if bm25_scores.max() > 0:
        bm25_scores = bm25_scores / (bm25_scores.max() + 1e-6)
    
    # Filter by BM25 cutoff
    valid_indices = np.where(bm25_scores > bm25_cutoff)[0]
    if len(valid_indices) == 0:
        valid_indices = np.argsort(-bm25_scores)[:top_n * 2]
    
    # Stage 2: Semantic reranking on filtered set
    filtered_bm25 = bm25_scores[valid_indices]
    
    query_emb = embedder.encode([query], normalize_embeddings=True)[0].astype(np.float32)
    filtered_embeddings = embeddings[valid_indices]
    cos_scores = filtered_embeddings @ query_emb
    
    # Normalize cosine scores to 0..1
    if len(cos_scores) > 0:
        cosn = (cos_scores - cos_scores.min()) / (cos_scores.max() - cos_scores.min() + 1e-6)
    else:
        cosn = cos_scores
    
    # Blend scores with optimized alpha
    blended = alpha * filtered_bm25 + (1 - alpha) * cosn
    
    # Return top_n by blended score
    top_local_idx = np.argsort(-blended)[:top_n]
    top_global_idx = valid_indices[top_local_idx]
    
    return [(int(i), float(blended[j])) for j, i in zip(top_local_idx, top_global_idx)]


def reciprocal_rank_fusion(
    bm25_results: List[Tuple[int, float]],
    semantic_results: List[Tuple[int, float]],
    k: int = 60,
) -> List[Tuple[int, float]]:
    """
    Reciprocal Rank Fusion (RRF) for combining multiple rankers.
    Better than simple averaging for combining different retrieval strategies.
    """
    # Convert to rank dicts
    bm25_ranks = {doc_id: (rank + 1) for rank, (doc_id, _) in enumerate(bm25_results)}
    semantic_ranks = {doc_id: (rank + 1) for rank, (doc_id, _) in enumerate(semantic_results)}
    
    # Get all unique doc_ids
    all_docs = set(bm25_ranks.keys()) | set(semantic_ranks.keys())
    
    # Calculate RRF scores
    rrf_scores = {}
    rho = 60  # Standard RRF constant
    for doc_id in all_docs:
        bm25_rank = bm25_ranks.get(doc_id, len(all_docs) + 1)
        semantic_rank = semantic_ranks.get(doc_id, len(all_docs) + 1)
        rrf_score = 1.0 / (rho + bm25_rank) + 1.0 / (rho + semantic_rank)
        rrf_scores[doc_id] = rrf_score
    
    # Sort by RRF score
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs[:k]
