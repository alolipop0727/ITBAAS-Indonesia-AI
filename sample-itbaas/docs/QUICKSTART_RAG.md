# Quickstart RAG — sample-itbaas

Dependency: hanya Python 3 stdlib. Untuk produksi, ganti `rank()` dengan BM25/embedding (e.g. `sentence-transformers`, `faiss`, `qdrant`).

```python
import json, re, math, collections
from pathlib import Path

chunks = [json.loads(l) for l in open('data/knowledge_chunks.jsonl', encoding='utf-8')]

def tokenize(s):
    return re.findall(r'[a-z0-9]{2,}', (s or '').lower())

# simple BM25-ish keyword score
df = collections.Counter()
docs = []
for c in chunks:
    toks = tokenize(c['title'] + ' ' + c['text'])
    docs.append(toks)
    for t in set(toks): df[t] += 1
N = len(docs)

def rank(query, k=5):
    q = tokenize(query)
    scores = []
    for i, toks in enumerate(docs):
        tf = collections.Counter(toks)
        s = 0.0
        for t in q:
            if t in tf:
                idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1)
                s += idf * (tf[t] / (tf[t] + 1.5))
        if s: scores.append((s, i))
    scores.sort(reverse=True, key=lambda x: x[0])
    return [chunks[i] for _, i in scores[:k]]

for c in rank('akreditasi S1 informatika'):
    print('-', c['title'], '|', c['url'])
    print(c['text'][:300], '\n')
```

## Field `knowledge_chunks.jsonl`
`id, source, source_type, wp_id, slug, title, url, date, modified, categories, tags, chunk_index, text`

## Strategi retrieval
1. Prefilter: jika query mengandung `pmb|daftar|pendaftaran|biaya|beasiswa|syarat`, prioritaskan `source_type=pmb_page` dan `source=itbaas.id` dengan kategori Beasiswa/Berita Kampus.
2. Hybrid: tambahkan exact-match dari `faq.jsonl` (cosine/BM25 atas question).
3. Selalu tampilkan `url` sumber di jawaban atau di debug panel.
4. Jangan retrieval dari `raw/` langsung; sudah diproses di JSONL.

## Contoh integrasi minimal (LLM)
```text
System: isi docs/agent_system_prompt.md
User: {pertanyaan}
Context: {top-k chunks dari rank(pertanyaan)}
Instruksi: jawab dari Context; jika tidak ada, arahkan ke PMB.
```
