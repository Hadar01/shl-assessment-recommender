from __future__ import annotations

import argparse
import pandas as pd

from shlrec.metrics import mean_metrics, recall_at_k, average_precision_at_k
from shlrec.recommender import Recommender
from shlrec.utils import canonical_shl_url

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", default="data/Gen_AI Dataset.xlsx", help="Path to Gen_AI Dataset.xlsx")
    p.add_argument("--index_dir", default="data/index", help="Index directory")
    args = p.parse_args()

    df = pd.read_excel(args.xlsx, sheet_name="Train-Set")
    df = df.dropna(subset=["Query", "Assessment_url"])

    # group relevant urls by query
    q2rel = {}
    for q, sub in df.groupby("Query"):
        urls = [canonical_shl_url(u) for u in sub["Assessment_url"].tolist()]
        q2rel[q] = sorted(set(urls))

    rec = Recommender(index_dir=args.index_dir)
    q2pred = {}
    
    print("\n" + "="*100)
    print("PER-QUERY BREAKDOWN".center(100))
    print("="*100)
    
    for q in sorted(q2rel.keys()):
        items = rec.recommend(q, k=10)
        q2pred[q] = [canonical_shl_url(it["url"]) for it in items]
        
        # Calculate per-query metrics
        rel = q2rel[q]
        pred = q2pred[q]
        r10 = recall_at_k(pred, rel, k=10)
        ap10 = average_precision_at_k(pred, rel, k=10)
        
        print(f"\nQuery: {q[:80]}...")
        print(f"  #Relevant: {len(rel)} | Recall@10: {r10:.1%} | MAP@10: {ap10:.4f}")
        print(f"  Predicted: {len(pred)} items")

    print("\n" + "="*100)
    metrics = mean_metrics(q2rel, q2pred, k=10)
    print(f"OVERALL METRICS: Recall@10={metrics['mean_recall@10']:.4f} | MAP@10={metrics['map@10']:.4f}".center(100))
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
