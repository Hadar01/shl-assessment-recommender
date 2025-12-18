from __future__ import annotations

import json
import time
import re
from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .utils import canonical_shl_url, normalize_whitespace, TEST_TYPE_MAP


@dataclass
class CatalogItem:
    name: str
    url: str
    description: str
    duration: int
    remote_support: str        # "Yes"/"No"
    adaptive_support: str      # "Yes"/"No"
    test_type: List[str]       # list of human-readable strings

    # Useful debug / provenance
    raw_test_type: List[str] | None = None


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch(session: requests.Session, url: str, timeout: int = 120) -> str:
    url = url.replace("http://", "https://")
    r = session.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)

    # If SHL/CloudFront returns an error page, fail with a helpful message
    if r.status_code >= 400:
        snippet = (r.text or "")[:500]
        raise RuntimeError(f"HTTP {r.status_code} for {url}\nFirst 500 chars:\n{snippet}")

    if not isinstance(r.text, str) or not r.text.strip():
        raise RuntimeError(f"Empty response body for {url} (status {r.status_code})")

    return r.text




def _extract_listing_rows(html: str, base_url: str) -> List[Tuple[str, str, Optional[bool], Optional[bool], List[str]]]:
    """Extract (name, url, remote?, adaptive?, test_type_letters[]) from a catalog listing page.

    This is written defensively because the catalog markup has changed over time.
    """
    soup = BeautifulSoup(html, "lxml")

    rows = []

    # Heuristic: any anchor containing /product-catalog/view/ is a product link.
    # We'll try to recover row context (remote/adaptive/test type) from the parent row.
    anchors = soup.select('a[href*="/product-catalog/view/"]')
    for a in anchors:
        href = a.get("href") or ""
        name = normalize_whitespace(a.get_text(" ", strip=True))
        if not href or not name:
            continue
        abs_url = urljoin(base_url, href)

        # Grab nearby text to infer test type letters (K/P/etc.)
        parent_text = normalize_whitespace(a.parent.get_text(" ", strip=True)) if a.parent else ""
        # Sometimes the row text includes letters like "K P" etc.
        letters = re.findall(r"\b[A-Z]\b", parent_text)
        letters = [l for l in letters if l in TEST_TYPE_MAP]

        # Try to infer booleans from icons/aria labels within the same row/container.
        remote = adaptive = None
        container = a.find_parent(["tr", "li", "div"])
        if container:
            # Look for any aria-label/alt with yes/no
            blob = " ".join(
                [str(container.get("aria-label") or ""), str(container.get("title") or "")]
            ).lower()
            # Also include alt texts
            for img in container.select("img[alt]"):
                blob += " " + (img.get("alt") or "").lower()
            if "remote" in blob and "yes" in blob:
                remote = True
            if "remote" in blob and "no" in blob:
                remote = False
            if "adaptive" in blob and "yes" in blob:
                adaptive = True
            if "adaptive" in blob and "no" in blob:
                adaptive = False

            # Common pattern: a check icon exists => True
            if remote is None:
                # crude: if cell has checkmark svg/icon near a 'Remote' header, hard to generalize
                pass

        rows.append((name, abs_url, remote, adaptive, letters))

    # Deduplicate by URL while keeping first occurrence
    seen = set()
    out = []
    for r in rows:
        if r[1] in seen:
            continue
        seen.add(r[1])
        out.append(r)
    return out


def _parse_detail_page(html: str) -> Tuple[str, str, int, List[str], Optional[bool], Optional[bool]]:
    """Parse (name, description, duration_minutes, test_type_names, remote?, adaptive?) from a product page."""
    soup = BeautifulSoup(html, "lxml")
    text = normalize_whitespace(soup.get_text(" ", strip=True))

    # Name: try h1 first, else title
    name = ""
    h1 = soup.find("h1")
    if h1:
        name = normalize_whitespace(h1.get_text(" ", strip=True))
    if not name:
        title = soup.find("title")
        if title:
            name = normalize_whitespace(title.get_text(" ", strip=True)).replace("| SHL", "").strip()

    # Description: heuristic extraction between "Description" and next known section
    desc = ""
    m = re.search(r"\bDescription\b\s+(.*?)(?:\bJob levels\b|\bLanguages\b|\bAssessment length\b|\bTest Type\b|Back to Product Catalog|All rights reserved\.|$)", text, flags=re.IGNORECASE)
    if m:
        desc = m.group(1).strip()
    if not desc:
        # fallback: meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            desc = normalize_whitespace(meta["content"])

    # Duration: extract from 'Approximate Completion Time in minutes = X' or range 'X to Y'
    duration = 0
    m = re.search(r"Approximate Completion Time in minutes\s*=\s*(\d+)(?:\s*to\s*(\d+))?", text, flags=re.IGNORECASE)
    if m:
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        duration = max(lo, hi)
    else:
        # Sometimes shown as 'Assessment length ... = 19'
        m2 = re.search(r"Assessment length\s+Approximate Completion Time in minutes\s*=\s*(\d+)", text, flags=re.IGNORECASE)
        if m2:
            duration = int(m2.group(1))

    # Test Type: 'Test Type: K' or list of letters
    test_types: List[str] = []
    m = re.search(r"Test Type\s*:\s*([A-Z](?:\s*[A-Z])*)", text)
    if m:
        letters = re.findall(r"[A-Z]", m.group(1))
        test_types = [TEST_TYPE_MAP.get(l, l) for l in letters if l in TEST_TYPE_MAP]

    # Remote & adaptive: hard to parse reliably from plain text if icons are used.
    # We attempt text-based inference as fallback.
    remote = None
    adaptive = None
    if re.search(r"\badaptive\b|\bIRT\b", desc, flags=re.IGNORECASE):
        adaptive = True

    return name, desc, duration, test_types, remote, adaptive


def scrape_individual_test_solutions(
    base_url: str,
    out_jsonl_path: str,
    min_expected: int = 377,
    start_step: int = 12,
    max_pages: int = 200,
    sleep_s: float = 0.2,
) -> int:
    """Scrape Individual Test Solutions (type=1) and write JSONL.

    Returns number of scraped items.
    """
    session = requests.Session()
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    retry = Retry(
            total=10,
            backoff_factor=2.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)


    # 1) Collect product URLs from listing pages
    product_rows: List[Tuple[str, str, Optional[bool], Optional[bool], List[str]]] = []
    seen_urls: Set[str] = set()

    empty_pages = 0
    for page_idx in range(max_pages):
        start = page_idx * start_step
        params = {"type": 1, "start": start}
        url = base_url.rstrip("/") + "/?" + urlencode(params)
        try:
            html = _fetch(session, url)
        except Exception as e:
            # Sometimes the trailing slash style differs; retry without extra slash.
            alt = base_url.rstrip("/") + "?" + urlencode(params)
            html = _fetch(session, alt)

        rows = _extract_listing_rows(html, base_url)
        new_rows = [r for r in rows if r[1] not in seen_urls]
        if not new_rows:
            empty_pages += 1
            # break after 2 consecutive empties
            if empty_pages >= 2:
                break
        else:
            empty_pages = 0
        for r in new_rows:
            seen_urls.add(r[1])
            product_rows.append(r)

        time.sleep(sleep_s)

    if len(product_rows) < min_expected:
        raise RuntimeError(
            f"Only found {len(product_rows)} product links from listing pages. "
            f"Expected at least {min_expected}. "
            f"Try increasing max_pages or using the alternate base URL."
        )

    # 2) Fetch details
    items: List[CatalogItem] = []
    for (name_guess, url, remote_guess, adaptive_guess, letters_guess) in tqdm(product_rows, desc="Fetching product pages"):
        try:
            html = _fetch(session, url)
        except Exception:
            # try canonical /products/ URL if needed
            canon = canonical_shl_url(url)
            html = _fetch(session, canon)
            url = canon

        name, desc, duration, test_types, remote, adaptive = _parse_detail_page(html)

        # Merge listing inferences
        if not test_types and letters_guess:
            test_types = [TEST_TYPE_MAP.get(l, l) for l in letters_guess]

        remote_support = "Yes" if (remote if remote is not None else (remote_guess if remote_guess is not None else True)) else "No"
        adaptive_support = "Yes" if (adaptive if adaptive is not None else (adaptive_guess if adaptive_guess is not None else False)) else "No"

        item = CatalogItem(
            name=name or name_guess,
            url=canonical_shl_url(url),
            description=desc,
            duration=int(duration or 0),
            remote_support=remote_support,
            adaptive_support=adaptive_support,
            test_type=test_types,
            raw_test_type=letters_guess or None,
        )
        items.append(item)
        time.sleep(sleep_s)

    # 3) Write JSONL
    with open(out_jsonl_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(asdict(it), ensure_ascii=False) + "\n")

    return len(items)
