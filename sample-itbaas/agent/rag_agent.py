#!/usr/bin/env python3
# sample-itbaas offline RAG agent: public ITB AAS KB retrieval + fail-closed answers. No network, no LLM keys required.
import json, re, math, argparse, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

STOP = set('yang dan di ke dari untuk dengan pada adalah itu ini atau dan nya saya anda kami kita mau tolong dong gimana apa saja berapa'.split())
BLOCK = ['system prompt','ignore previous','jailbreak','developer mode','.env','api key','password','token','raw/','internal','bocor','dump','credential','admin override','bypass']
OFFICIAL = 'PMB: https://pmb.itbaas.ac.id/ | WA +62 857-9920-5711 / 0889-8337-3916 | email pmb@itbaas.ac.id | telp (0271) 726156'

def load_json(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))

def load_jsonl(name):
    return [json.loads(l) for l in (DATA / name).read_text(encoding='utf-8').splitlines() if l.strip()]

PROFILE = load_json('campus-profile.json')
PROGRAMS = load_json('programs.json')
ADMISSION = load_json('admission.json')
UKM = load_json('ukm.json')
FAQ = load_jsonl('faq.jsonl')
CHUNKS = load_jsonl('knowledge_chunks.jsonl')

def toks(s):
    return [t for t in re.findall(r'[a-z0-9]{2,}', (s or '').lower()) if t not in STOP]

DF = collections.Counter()
DOCS = []
for c in CHUNKS:
    t = toks((c.get('title','') + ' ' + c.get('text','')))
    DOCS.append(t)
    for x in set(t): DF[x] += 1
N = len(DOCS)
AVG = sum(map(len, DOCS)) / max(N, 1)
K1, B = 1.4, 0.72

def bm25(query, top=4):
    q = toks(query)
    scores = []
    for i, d in enumerate(DOCS):
        tf = collections.Counter(d)
        s = 0.0
        for t in q:
            if t in tf:
                idf = math.log((N - DF[t] + 0.5) / (DF[t] + 0.5) + 1)
                s += idf * (tf[t] * (K1 + 1)) / (tf[t] + K1 * (1 - B + B * len(d) / AVG))
        if s > 0: scores.append((s, i))
    scores.sort(reverse=True, key=lambda x: x[0])
    return [(s, CHUNKS[i]) for s, i in scores[:top]]

def faq_match(query):
    q = set(toks(query))
    best = (0.0, None)
    for f in FAQ:
        fq = set(toks(f.get('q','')))
        if not fq: continue
        score = len(q & fq) / max(len(q | fq), 1)
        if score > best[0]: best = (score, f)
    return best

def official_address():
    ids = PROFILE['identity']
    campuses = ids.get('campuses', [])
    lines = [f"Kampus 1: {ids['address']}"]
    for c in campuses:
        if c.get('name') == 'Kampus 2': lines.append(f"Kampus 2: {c['address']}")
    lines.append(OFFICIAL)
    return '\n'.join(lines)

def official_contacts():
    c = PROFILE['contacts']
    return (f"Alamat: {PROFILE['identity']['address']}\nTelp: {PROFILE['identity']['phone']}\n"
            f"WA umum: {c['general_whatsapp']} | admin PMB: {c['pmb_whatsapp_admin']}\n"
            f"Email: {c['email_general']} | {c['email_info']} | {c['email_pmb']}\n{OFFICIAL}")

def program_list():
    return '\n'.join(
        f"- {p['level']} {p['name']} — {p['faculty']} (PMB id {p['pmb_id']})" for p in PROGRAMS)

def ukm_list():
    return '\n'.join(f"- {o['name']}: {o['focus']} ({o['instagram']})" for o in UKM['organizations'])

def blocked(query):
    q = query.lower()
    return any(p in q for p in BLOCK)

def refuse():
    return {
        'answer': 'Bagian itu bukan informasi publik yang bisa saya berikan. Saya bisa bantu info publik ITB AAS: PMB, prodi, biaya resmi yang tercantum, kontak, UKM. Untuk urusan administratif/internal, hubungi PMB/admin resmi.',
        'sources': ['docs/agent_system_prompt.md'],
        'confidence': 'blocked'
    }

def route(query):
    q = query.lower()
    if blocked(q): return refuse()
    if any(k in q for k in ['alamat', 'lokasi', 'kampus 1', 'kampus 2']):
        return {'answer': official_address(), 'sources': ['data/campus-profile.json'], 'confidence': 'direct'}
    if any(k in q for k in ['wa', 'whatsapp', 'no hp', 'nomor', 'kontak', 'telp', 'telepon', 'email']):
        return {'answer': official_contacts(), 'sources': ['data/campus-profile.json'], 'confidence': 'direct'}
    if any(k in q for k in ['program studi', 'prodi', 'jurusan', 'fakultas']):
        return {'answer': program_list(), 'sources': ['data/programs.json'], 'confidence': 'direct'}
    if 'ukm' in q or 'hima' in q or 'bem' in q:
        return {'answer': ukm_list(), 'sources': ['data/ukm.json'], 'confidence': 'direct'}
    if 'biaya pendaftaran' in q or 'daftar bayar' in q:
        return {'answer': f"Biaya pendaftaran Rp{ADMISSION['registration_fee_idr']:,} (transfer/tunai). Jalur KIP-K tercantum GRATIS di PMB; jalur lain berbayar. Biaya kuliah bisa berubah—konfirmasi ke PMB.\n{OFFICIAL}", 'sources': ['data/admission.json', 'https://pmb.itbaas.ac.id/jalur-seleksi'], 'confidence': 'direct'}
    return None

def answer(query):
    r = route(query)
    if r: return r
    fs, f = faq_match(query)
    if f and fs >= 0.34:
        return {'answer': f['a'], 'sources': [f.get('source', 'data/faq.jsonl')], 'confidence': 'faq' if fs < 0.55 else 'faq_strong'}
    hits = bm25(query, top=4)
    if not hits or hits[0][0] < 2.0:
        return {'answer': f'Saya belum punya data resmi untuk itu. Konfirmasi ke {OFFICIAL}', 'sources': [], 'confidence': 'low'}
    ctx = '\n\n'.join(f"- {h['title']}: {h['text'][:420]}" for _, h in hits)
    return {'answer': f'Berdasarkan KB publik:\n{ctx}\n\nUntuk keputusan resmi, konfirmasi ke {OFFICIAL}', 'sources': [h['url'] for _, h in hits], 'confidence': 'kb'}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('query', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    q = ' '.join(args.query)
    out = answer(q)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(out['answer'])
        if out.get('sources'):
            print('\nSumber:')
            for s in out['sources']: print('-', s)
        print('confidence:', out['confidence'])
