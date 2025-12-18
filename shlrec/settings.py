from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# CRITICAL FIX: Load .env file automatically
load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Base URLs
    # NOTE: SHL sometimes uses /products/product-catalog and sometimes /solutions/products/product-catalog.
    # We keep both and canonicalize URLs for evaluation.
    shl_catalog_base: str = os.getenv("SHL_CATALOG_BASE", "https://www.shl.com/solutions/products/product-catalog/")
    shl_catalog_base_alt: str = os.getenv("SHL_CATALOG_BASE_ALT", "https://www.shl.com/products/product-catalog/")

    # Storage
    index_dir: Path = Path(os.getenv("INDEX_DIR", "data/index"))

    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Retrieval params
    hybrid_alpha: float = float(os.getenv("HYBRID_ALPHA", "0.39"))  # BM25 weight (fine-tuned: 0.39)
    candidate_pool: int = int(os.getenv("CANDIDATE_POOL", "200"))   # INCREASED: was 60, now 200 for better coverage
    top_k: int = int(os.getenv("TOP_K", "10"))                      # final k returned

    # Optional rerank
    rerank_with_gemini: bool = os.getenv("RERANK_WITH_GEMINI", "0") in ("1", "true", "True")


def get_settings() -> Settings:
    return Settings()
