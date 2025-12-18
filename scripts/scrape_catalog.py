from __future__ import annotations

import argparse
from shlrec.catalog_scraper import scrape_individual_test_solutions
from shlrec.settings import get_settings

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/catalog.jsonl", help="Output JSONL path")
    p.add_argument("--base_url", default=None, help="Override catalog base URL")
    args = p.parse_args()

    s = get_settings()
    base_url = args.base_url or s.shl_catalog_base

    n = scrape_individual_test_solutions(base_url=base_url, out_jsonl_path=args.out, sleep_s=1.0, max_pages=350)
    print(f"Scraped {n} items -> {args.out}")

if __name__ == "__main__":
    main()
