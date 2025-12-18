from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .settings import Settings
from .utils import DiskJSONCache, safe_json_loads


PROMPT_TEMPLATE = """You are an information extraction system.
Given a hiring query or job description, extract constraints and intent.

Return ONLY valid JSON with this schema:
{{
  "hard_skills": [string],
  "soft_skills": [string],
  "roles": [string],
  "seniority": "intern|junior|mid|senior|lead|unknown",
  "duration_limit_minutes": integer|null,
  "remote_required": true|false|null,
  "domain_mix": {{
     "K": float,
     "P": float
  }}
}}

Rules:
- If query includes both technical + collaboration/communication/stakeholders/teamwork, set K and P both > 0 with a balanced mix.
- If query is purely technical, set K high and P low but not zero.
- If duration is mentioned, extract it as minutes.
- Output JSON only. No markdown.

QUERY:
<<<{user_query}>>>
"""


@dataclass
class Intent:
    hard_skills: list[str]
    soft_skills: list[str]
    roles: list[str]
    seniority: str
    duration_limit_minutes: Optional[int]
    remote_required: Optional[bool]
    domain_mix: Dict[str, float]


def heuristic_intent(query: str) -> Intent:
    q = (query or "").lower()
    # duration
    dur = None
    import re
    m = re.search(r"(\d+)\s*(?:min|mins|minutes)", q)
    if m:
        dur = int(m.group(1))
    # soft-skill presence
    soft = any(w in q for w in ["collabor", "stakeholder", "communication", "team", "leadership", "behavior", "personality"])
    if soft:
        mix = {"K": 0.6, "P": 0.4}
    else:
        mix = {"K": 0.9, "P": 0.1}
    return Intent(
        hard_skills=[],
        soft_skills=[],
        roles=[],
        seniority="unknown",
        duration_limit_minutes=dur,
        remote_required=None,
        domain_mix=mix,
    )


class GeminiIntentExtractor:
    def __init__(self, settings: Settings, cache_path: str = "data/index/gemini_cache.json"):
        self.settings = settings
        self.cache = DiskJSONCache(cache_path)

        self._model = None

    def _lazy_init(self):
        if self._model is not None:
            return
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Put it in .env or env vars.")
        import google.generativeai as genai
        genai.configure(api_key=self.settings.gemini_api_key)
        self._model = genai.GenerativeModel(self.settings.gemini_model)

    def extract(self, query: str) -> Intent:
        key = f"intent::{self.settings.gemini_model}::{query}"
        cached = self.cache.get(key)
        if isinstance(cached, dict) and "domain_mix" in cached:
            return self._to_intent(cached)

        try:
            self._lazy_init()
            prompt = PROMPT_TEMPLATE.format(user_query=query)
            resp = self._model.generate_content(prompt)
            obj = safe_json_loads(getattr(resp, "text", "") or "")
            if not obj:
                raise ValueError("Gemini returned non-JSON")
            self.cache.set(key, obj)
            return self._to_intent(obj)
        except Exception:
            # fallback to heuristic
            return heuristic_intent(query)

    def _to_intent(self, obj: Dict[str, Any]) -> Intent:
        domain_mix = obj.get("domain_mix") or {}
        # normalize
        k = float(domain_mix.get("K", 0.8))
        p = float(domain_mix.get("P", 0.2))
        s = max(k + p, 1e-6)
        domain_mix = {"K": k / s, "P": p / s}

        dur = obj.get("duration_limit_minutes")
        try:
            dur = int(dur) if dur is not None else None
        except Exception:
            dur = None

        remote = obj.get("remote_required")
        if remote not in (True, False, None):
            remote = None

        return Intent(
            hard_skills=list(obj.get("hard_skills") or []),
            soft_skills=list(obj.get("soft_skills") or []),
            roles=list(obj.get("roles") or []),
            seniority=str(obj.get("seniority") or "unknown"),
            duration_limit_minutes=dur,
            remote_required=remote,
            domain_mix=domain_mix,
        )
