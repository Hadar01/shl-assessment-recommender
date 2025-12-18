from __future__ import annotations

import argparse
import pandas as pd

from shlrec.recommender import Recommender
from shlrec.utils import canonical_shl_url

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", default="data/Gen_AI Dataset.xlsx", help="Path to Gen_AI Dataset.xlsx")
    p.add_argument("--index_dir", default="data/index", help="Index directory")
    p.add_argument("--out", default="predictions.csv", help="Output CSV path")
    args = p.parse_args()

    df = pd.read_excel(args.xlsx, sheet_name="Test-Set")
    df = df.dropna(subset=["Query"])
    queries = df["Query"].tolist()

    rec = Recommender(index_dir=args.index_dir)

    rows = []
    for q in queries:
        items = rec.recommend(q, k=10)
        for it in items:
            rows.append({"Query": q, "Assessment_url": canonical_shl_url(it["url"])})

    out_df = pd.DataFrame(rows, columns=["Query", "Assessment_url"])
    out_df.to_csv(args.out, index=False)
    print(f"Wrote {len(out_df)} rows -> {args.out}")

if __name__ == "__main__":
    main()
