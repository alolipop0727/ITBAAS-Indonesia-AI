#!/usr/bin/env python3
import json, re, html, csv, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
for src in ['itbaas-id-wp-pages.json','wp-pages.json']:
    p = ROOT/'raw'/src
    d = json.load(open(p, encoding='utf-8'))
    x = next((i for i in d if i.get('slug') == 'unduh'), None)
    if not x: continue
    s = x.get('content',{}).get('rendered','')
    rows = re.findall(r'<tr>(.*?)</tr>', s, re.S)
    out = []
    for row in rows:
        cells = re.findall(r'<td.*?>(.*?)</td>', row, re.S)
        if len(cells) < 3: continue
        clean = lambda c: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(c))).strip()
        label = clean(cells[1])
        m = re.search(r'href="([^"]+)"', cells[2])
        link = html.unescape(m.group(1)) if m else ''
        if label and link: out.append({'source_page': x.get('link'), 'label': label, 'url': link})
    seen=set(); final=[]
    for r in out:
        key=(r['label'], r['url'])
        if key not in seen:
            seen.add(key); final.append(r)
    with open(ROOT/'data/downloads.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['label','url','source_page']); w.writeheader()
        for r in final: w.writerow(r)
    print('downloads', len(final), ROOT/'data/downloads.csv')
    break
