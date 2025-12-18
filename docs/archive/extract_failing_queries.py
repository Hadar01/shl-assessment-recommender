import pandas as pd
from shlrec.utils import canonical_shl_url

df = pd.read_excel('data/Gen_AI Dataset.xlsx', sheet_name='Train-Set')
df = df.dropna(subset=['Query', 'Assessment_url'])

# Query indices for the 3 failing queries (0% recall)
failing_indices = [6, 8, 9]  # Based on earlier output: Consultant, 1-hour job, Admin

for idx in failing_indices:
    q = df['Query'].unique()[idx - 1]
    print('\n' + '='*100)
    print(f'FAILING QUERY (Query {idx}):')
    print('='*100)
    print(f'\nFull Query Text:\n{q}')
    
    urls = df[df['Query'] == q]['Assessment_url'].unique()
    print(f'\nGround Truth ({len(urls)} relevant assessments):')
    for url in urls:
        canonical = canonical_shl_url(url)
        print(f'  - {canonical}')
