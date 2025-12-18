from __future__ import annotations

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .utils import normalize_whitespace


def looks_like_url(text: str) -> bool:
    return bool(re.match(r"^https?://", (text or "").strip(), flags=re.IGNORECASE))


def extract_text_from_url(url: str, timeout: int = 30) -> str:
    """Very simple JD extractor: fetch HTML and return visible text."""
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # drop scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    return normalize_whitespace(text)
