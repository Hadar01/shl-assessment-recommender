"""Fine-grained parameter tuning with improved balancing."""
from shlrec.settings import Settings
from shlrec.retrieval import load_index, hybrid_retrieve
from shlrec.llm_gemini import GeminiIntentExtractor
from shlrec.balancing_improved import pick_balanced_improved
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

print("Testing fine-tuned alpha values with improved balancing...")
print("alpha | recall@10 | map@10")
print("-" * 35)

best_recall = 0
best_params = {}

for alpha in [0.38, 0.39, 0.40, 0.41, 0.42, 0.43]:
    q2pred = {}
    for q in q2rel.keys():
        intent = intent_extractor.extract(q)
        pairs = hybrid_retrieve(idx, q, alpha=alpha, top_n=60)
        
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
        q2pred[q] = [canonical_shl_url(it['url']) for it in out]
    
    metrics = mean_metrics(q2rel, q2pred, k=10)
    recall = metrics['mean_recall@10']
    map_score = metrics['map@10']
    print(f"{alpha:.2f} | {recall:9.4f} | {map_score:6.4f}")
    
    if recall > best_recall:
        best_recall = recall
        best_params = {'alpha': alpha, 'metrics': metrics}

print("-" * 35)
print(f"Best: alpha={best_params.get('alpha', 0.40):.2f}")
print(f"  Recall: {best_params.get('metrics', {}).get('mean_recall@10', 0):.4f}")
print(f"  MAP:    {best_params.get('metrics', {}).get('map@10', 0):.4f}")
