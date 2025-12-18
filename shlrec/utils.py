from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional


TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations",
}

SOFT_SKILL_HINTS = {
    "collaborat", "stakeholder", "communication", "team", "leadership", "influenc",
    "conflict", "customer", "relationship", "people", "manager", "coaching",
    "negotiat", "presentation", "empathy", "behavior", "behaviour", "personality",
}


def canonical_shl_url(url: str) -> str:
    """Canonicalize SHL catalog URLs so /solutions/... and /products/... compare equal."""
    url = (url or "").strip()
    if not url:
        return url
    m = re.search(r"/product-catalog/view/([^/?#]+)/?", url)
    if not m:
        # fallback: normalize trailing slash
        return url.rstrip("/") + "/"
    slug = m.group(1)
    return f"https://www.shl.com/products/product-catalog/view/{slug}/"


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from a model response. Attempts to extract the first {...} block."""
    if not text:
        return None
    text = text.strip()

    # Fast path: valid JSON already
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Try to find a JSON object substring
    m = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(1))
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None
    return None


class DiskJSONCache:
    """Tiny disk cache for Gemini calls to reduce free-tier usage."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def get(self, key: str) -> Optional[dict]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return data.get(key)

    def set(self, key: str, value: dict) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data[key] = value
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
