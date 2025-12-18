from __future__ import annotations

import argparse
from shlrec.indexer import build_index

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", default="data/catalog.jsonl", help="Catalog JSONL path")
    p.add_argument("--index_dir", default="data/index", help="Index output dir")
    p.add_argument("--embedding_model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = p.parse_args()

    build_index(args.catalog, args.index_dir, embedding_model=args.embedding_model)
    print(f"Index built at {args.index_dir}")

if __name__ == "__main__":
    main()
