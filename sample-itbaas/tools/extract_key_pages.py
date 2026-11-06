#!/usr/bin/env python3
import json, re, html, pathlib
from html.parser import HTMLParser
ROOT = pathlib.Path(__file__).resolve().parents[1]
class T(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self, t, a):
        if t in ('script','style'): self.skip += 1
        if t in ('p','div','br','li','tr','h1','h2','h3','h4','table'): self.parts.append('\n')
    def handle_endtag(self, t):
        if t in ('script','style'): self.skip = max(0, self.skip - 1)
        if t in ('p','div','li','tr','h1','h2','h3','h4'): self.parts.append('\n')
    def handle_data(self, d):
        if not self.skip: self.parts.append(d)
def txt(s):
    p = T(); p.feed(s or '')
    t = html.unescape(''.join(p.parts)).replace('\xa0',' ')
    return re.sub(r'\n\s*\n+','\n\n', re.sub(r'[ \t]+',' ', t)).strip()
out = []
for name, path in [('id', ROOT/'raw/itbaas-id-wp-pages.json'), ('ac', ROOT/'raw/wp-pages.json')]:
    data = json.load(open(path, encoding='utf-8'))
    out.append(f'\n### {name}')
    for slug in ['about','visi-misi','sejarah','profil','struktur-organisasi','informasi-pmb','syarat-pendaftaran-2','beasiswa-itb-aas-indonesia','beasiswa-copy','beasiswa-2','s2-manajemen','unduh','contact']:
        hit = next((x for x in data if x.get('slug') == slug), None)
        if not hit: continue
        out.append(f'\n## {slug} | {txt(hit.get("title",{}).get("rendered",""))}')
        out.append(txt(hit.get('content',{}).get('rendered',''))[:8000])
(ROOT/'data/key-pages.txt').write_text('\n'.join(out), encoding='utf-8')
print(ROOT/'data/key-pages.txt', (ROOT/'data/key-pages.txt').stat().st_size)
