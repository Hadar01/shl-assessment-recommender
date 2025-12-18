import json
from shlrec.corpus_enrichment import build_enriched_corpus_text

# Load first few catalog items
with open('data/catalog.jsonl', 'r') as f:
    items = []
    for i, line in enumerate(f):
        if i >= 3:
            break
        items.append(json.loads(line))

# Check enriched corpus
for item in items:
    enriched = build_enriched_corpus_text(item)
    print(f"Name: {item['name']}")
    print(f"Test Types: {item.get('test_type', [])}")
    print(f"Enriched (first 500 chars):\n{enriched[:500]}\n")
    print("=" * 80)
