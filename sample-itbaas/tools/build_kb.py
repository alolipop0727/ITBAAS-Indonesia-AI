#!/usr/bin/env python3
# sample-itbaas knowledge-base builder: merges public ITB AAS sources into RAG-ready JSONL + inventories.
import json, re, html, csv, hashlib, pathlib, datetime
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT/'raw'; DATA = ROOT/'data'; PAGES = ROOT/'pages'; DATA.mkdir(exist_ok=True)

class TextExtract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.skip=0; self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript','svg'): self.skip += 1
        if tag in ('p','div','br','li','tr','h1','h2','h3','h4','table','section','article'): self.parts.append('\n')
        if tag in ('td','th'): self.parts.append(' | ')
    def handle_endtag(self, tag):
        if tag in ('script','style','noscript','svg'): self.skip=max(0,self.skip-1)
        if tag in ('p','div','li','tr','h1','h2','h3','h4'): self.parts.append('\n')
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def strip_html(s):
    p=TextExtract(); p.feed(s or '')
    t=html.unescape(''.join(p.parts))
    t=t.replace('\xa0',' ')
    t=re.sub(r'[ \t\r\f\v]+',' ',t)
    t=re.sub(r'\n\s*\n+','\n\n',t)
    return t.strip()

def norm_title(x): return strip_html(x.get('title',{}).get('rendered','')).strip()
def norm_content(x): return strip_html(x.get('content',{}).get('rendered',''))
def clean_url(u): return (u or '').strip()

def load_map(name):
    p=RAW/name; 
    if not p.exists(): return {}
    try: return {int(x['id']): strip_html(x.get('name','')) for x in json.load(open(p,encoding='utf-8'))}
    except Exception: return {}

cat_id = load_map('itbaas-id-wp-categories.json') | load_map('wp-categories.json')
tag_id = load_map('itbaas-id-wp-tags.json') | load_map('wp-tags.json')

def cat_names(ids): return [cat_id.get(i,str(i)) for i in ids or []]
def tag_names(ids): return [tag_id.get(i,str(i)) for i in ids or []]

def wp_items(primary, secondary, kind):
    prim=json.load(open(RAW/primary,encoding='utf-8'))
    sec=json.load(open(RAW/secondary,encoding='utf-8')) if (RAW/secondary).exists() else []
    seen={x.get('slug') for x in prim}
    items=[]
    for x in prim: items.append(('id',x))
    for x in sec:
        if x.get('slug') not in seen: items.append(('ac.id',x))
    out=[]
    for dom,x in items:
        title=norm_title(x); body=norm_content(x)
        if len(body) < 40: continue
        out.append({
            'source': 'itbaas.id' if dom=='id' else 'itbaas.ac.id',
            'source_type': 'wordpress_'+kind,
            'wp_id': x.get('id'), 'slug': x.get('slug'), 'title': title,
            'url': clean_url(x.get('link')), 'date': x.get('date'), 'modified': x.get('modified'),
            'categories': cat_names(x.get('categories')), 'tags': tag_names(x.get('tags')),
            'text': body,
        })
    return out

items = wp_items('itbaas-id-wp-pages.json','wp-pages.json','page') + wp_items('itbaas-id-wp-posts.json','wp-posts.json','post')

# PMB public app pages, saved as HTML then extracted to text
url_by_pmb = {
 'pmb_home.html':'https://pmb.itbaas.ac.id/',
 'pmb_program-studi.html':'https://pmb.itbaas.ac.id/program-studi',
 'pmb_jalur-seleksi.html':'https://pmb.itbaas.ac.id/jalur-seleksi',
 'pmb_pengumuman.html':'https://pmb.itbaas.ac.id/pengumuman',
 'pmb_daftar-informasi.html':'https://pmb.itbaas.ac.id/daftar-informasi',
 'pmb_user-guide.html':'https://pmb.itbaas.ac.id/user-guide',
 'pmb_informasi_1_kebijakan-dan-prosedur-pmb-itb-aas-adalah-sebagai-berikut.html':'https://pmb.itbaas.ac.id/informasi/1/kebijakan-dan-prosedur-pmb-itb-aas-adalah-sebagai-berikut',
}
for p in PAGES.glob('pmb_*.html'):
    if p.name in url_by_pmb:
        url=url_by_pmb[p.name]
    elif p.name.startswith('pmb_program-studi-detail_detail_'):
        url='https://pmb.itbaas.ac.id/program-studi-detail/detail/'+p.name.removeprefix('pmb_program-studi-detail_detail_').removesuffix('.html')
    else:
        url='https://pmb.itbaas.ac.id/'+p.name.removeprefix('pmb_').removesuffix('.html')
    txt=strip_html(p.read_text(encoding='utf-8', errors='ignore'))
    title=next((ln.strip() for ln in txt.splitlines() if ln.strip()), p.stem)
    items.append({'source':'pmb.itbaas.ac.id','source_type':'pmb_page','wp_id':None,'slug':p.stem,'title':title[:120],'url':url,'date':None,'modified':None,'categories':[],'tags':[],'text':txt})

# Wikipedia reference, explicitly third-party
wiki=RAW/'wikipedia-itbaas.html'
if wiki.exists():
    items.append({'source':'id.wikipedia.org','source_type':'reference','wp_id':None,'slug':'institut-teknologi-bisnis-aas-indonesia','title':'Institut Teknologi Bisnis AAS Indonesia (Wikipedia)','url':'https://id.wikipedia.org/wiki/Institut_Teknologi_Bisnis_AAS_Indonesia','date':None,'modified':None,'categories':[],'tags':[],'text':strip_html(wiki.read_text(encoding='utf-8', errors='ignore'))})

def chunk_text(t, max_chars=1400, overlap=180):
    paras=[p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]
    chunks=[]; cur=''
    for p in paras:
        if len(p) > max_chars:
            if cur: chunks.append(cur.strip()); cur=''
            for i in range(0, len(p), max_chars-overlap): chunks.append(p[i:i+max_chars].strip())
            continue
        if len(cur)+len(p)+2 <= max_chars:
            cur = (cur+'\n\n'+p).strip()
        else:
            if cur: chunks.append(cur.strip())
            tail = chunks[-1][-overlap:] if chunks else ''
            cur = (tail+'\n\n'+p).strip()
    if cur.strip(): chunks.append(cur.strip())
    return [c for c in chunks if len(c) > 30]

chunks=[]
for item in items:
    for i,c in enumerate(chunk_text(item['text'])):
        cid=hashlib.sha1((item['source']+item['url']+str(i)+c[:80]).encode()).hexdigest()[:16]
        chunks.append({'id':cid, **{k:item[k] for k in ['source','source_type','wp_id','slug','title','url','date','modified','categories','tags']}, 'chunk_index':i, 'text':c})

with open(DATA/'knowledge_chunks.jsonl','w',encoding='utf-8') as f:
    for c in chunks: f.write(json.dumps(c, ensure_ascii=False)+'\n')
with open(DATA/'corpus.txt','w',encoding='utf-8') as f:
    for c in chunks:
        f.write(f"### {c['title']}\nsource: {c['source']} | url: {c['url']} | type: {c['source_type']}\n{c['text']}\n\n")
with open(DATA/'items_inventory.json','w',encoding='utf-8') as f:
    json.dump([{k:v for k,v in it.items() if k!='text'} | {'chars':len(it['text'])} for it in items], f, ensure_ascii=False, indent=2)
with open(DATA/'items_inventory.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['source','source_type','wp_id','slug','title','url','date','modified','categories','tags','chars'])
    w.writeheader()
    for it in items:
        w.writerow({k:('; '.join(v) if isinstance(v,list) else v) for k,v in it.items() if k!='text'} | {'chars':len(it['text'])})
manifest={
    'name':'sample-itbaas-kb', 'built_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'sources':sorted({i['source'] for i in items}), 'items':len(items), 'chunks':len(chunks),
    'chunks_file':'data/knowledge_chunks.jsonl', 'corpus_file':'data/corpus.txt',
    'selection':'itbaas.id canonical; itbaas.ac.id-only slugs merged; PMB and Wikipedia included',
    'notes':['Public data only; no authenticated SIAKAD/PDDIKTI data.', 'Verify accreditation/current fees against official sources before publishing.'],
}
(DATA/'kb_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(manifest, ensure_ascii=False, indent=2))
print('total_text_chars', sum(len(i['text']) for i in items))
