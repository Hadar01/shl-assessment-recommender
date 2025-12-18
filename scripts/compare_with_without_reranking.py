"""Compare metrics with and without LLM reranking."""
from shlrec.settings import Settings
from shlrec.retrieval import load_index, hybrid_retrieve
from shlrec.llm_gemini import GeminiIntentExtractor
from shlrec.balancing_improved import pick_balanced_improved
from shlrec.llm_reranker import GeminiReranker
from shlrec.utils import canonical_shl_url
from shlrec.metrics import mean_metrics
import pandas as pd

# Load data
df = pd.read_excel('data/Gen_AI Dataset.xlsx', sheet_name='Train-Set')
df = df.dropna(subset=['Query', 'Assessment_url'])

q2rel = {}
for q, sub in df.groupby('Query'):
    urls = [canonical_shl_url(u) for u in sub['Assessment_url'].tolist()]
    q2rel[q] = sorted(set(urls))

# Load index
idx = load_index('data/index')
settings = Settings()
intent_extractor = GeminiIntentExtractor(settings, cache_path='data/index/gemini_cache.json')
reranker = GeminiReranker(settings)

print("=" * 60)
print("COMPARING: Without Reranking vs With Reranking")
print("=" * 60)

# Test WITHOUT reranking
print("\n[1] WITHOUT LLM RERANKING:")
q2pred_no_rerank = {}
for q in q2rel.keys():
    intent = intent_extractor.extract(q)
    pairs = hybrid_retrieve(idx, q, alpha=0.39, top_n=60)
    
    candidates = []
    for doc_id, score in pairs:
        it = dict(idx.meta[doc_id])
        it['_score'] = score
        it['url'] = canonical_shl_url(it.get('url', ''))
        it['adaptive_support'] = it.get('adaptive_support') or 'No'
        it['remote_support'] = it.get('remote_support') or 'Yes'
        it['duration'] = int(it.get('duration') or 0)
        it['test_type'] = list(it.get('test_type') or [])
        it['description'] = it.get('description') or ''
        it['name'] = it.get('name') or ''
        candidates.append(it)
    
    filtered = candidates
    if intent.duration_limit_minutes:
        under = [c for c in filtered if c.get('duration', 0) and c['duration'] <= intent.duration_limit_minutes]
        if len(under) >= 5:
            filtered = under
    if intent.remote_required is True:
        rem = [c for c in filtered if str(c.get('remote_support', '')).lower().startswith('y')]
        if len(rem) >= 5:
            filtered = rem
    
    out = pick_balanced_improved(filtered, k=10, kp_weights=intent.domain_mix)
    q2pred_no_rerank[q] = [canonical_shl_url(it['url']) for it in out]

metrics_no_rerank = mean_metrics(q2rel, q2pred_no_rerank, k=10)
print(f"  Recall@10: {metrics_no_rerank['mean_recall@10']:.4f}")
print(f"  MAP@10:    {metrics_no_rerank['map@10']:.4f}")

# Test WITH reranking
print("\n[2] WITH LLM RERANKING (50% weight):")
q2pred_rerank = {}
for q in q2rel.keys():
    intent = intent_extractor.extract(q)
    pairs = hybrid_retrieve(idx, q, alpha=0.39, top_n=60)
    
    candidates = []
    for doc_id, score in pairs:
        it = dict(idx.meta[doc_id])
        it['_score'] = score
        it['url'] = canonical_shl_url(it.get('url', ''))
        it['adaptive_support'] = it.get('adaptive_support') or 'No'
        it['remote_support'] = it.get('remote_support') or 'Yes'
        it['duration'] = int(it.get('duration') or 0)
        it['test_type'] = list(it.get('test_type') or [])
        it['description'] = it.get('description') or ''
        it['name'] = it.get('name') or ''
        candidates.append(it)
    
    filtered = candidates
    if intent.duration_limit_minutes:
        under = [c for c in filtered if c.get('duration', 0) and c['duration'] <= intent.duration_limit_minutes]
        if len(under) >= 5:
            filtered = under
    if intent.remote_required is True:
        rem = [c for c in filtered if str(c.get('remote_support', '')).lower().startswith('y')]
        if len(rem) >= 5:
            filtered = rem
    
    # RERANK with Gemini
    filtered = reranker.rerank(q, filtered, top_k=len(filtered))
    
    out = pick_balanced_improved(filtered, k=10, kp_weights=intent.domain_mix)
    q2pred_rerank[q] = [canonical_shl_url(it['url']) for it in out]

metrics_rerank = mean_metrics(q2rel, q2pred_rerank, k=10)
print(f"  Recall@10: {metrics_rerank['mean_recall@10']:.4f}")
print(f"  MAP@10:    {metrics_rerank['map@10']:.4f}")

# Comparison
print("\n" + "=" * 60)
print("IMPROVEMENT:")
print("=" * 60)
recall_diff = metrics_rerank['mean_recall@10'] - metrics_no_rerank['mean_recall@10']
map_diff = metrics_rerank['map@10'] - metrics_no_rerank['map@10']
recall_pct = (recall_diff / metrics_no_rerank['mean_recall@10']) * 100 if metrics_no_rerank['mean_recall@10'] > 0 else 0
map_pct = (map_diff / metrics_no_rerank['map@10']) * 100 if metrics_no_rerank['map@10'] > 0 else 0

print(f"Recall@10: {recall_diff:+.4f} ({recall_pct:+.1f}%)")
print(f"MAP@10:    {map_diff:+.4f} ({map_pct:+.1f}%)")

print("\n✅ Reranking is ready and working!" if recall_diff >= 0 else "\n⚠️ Reranking needs tuning")
