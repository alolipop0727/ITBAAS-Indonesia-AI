#!/usr/bin/env python3
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
path = ROOT/'data/faq.jsonl'
old_q = 'Kampus 1 itu di mana? Ada kampus 2?'
new_rows = [
  {"q":"Alamat Kampus 1 dan Kampus 2?","a":"Kampus 1: Jl. Slamet Riyadi No. 361 Windan, Makamhaji, Kartasura, Sukoharjo. Kampus 2: Jl. Hamzah Raya, Dusun III, Gumpang, Kec. Kartasura, Kabupaten Sukoharjo (post resmi menyebut Kampus 2/BLKK Yayasan Amaliyah Ilmi Surakarta; juga tertulis Jl. Hamzah Raya Kudusan Gumpang Kartasura).","source":"https://itbaas.id/asesmen-lapangan-program-studi-s1-akuntansi/"},
  {"q":"Kebidanan kuliah di Wonogiri?","a":"Tidak. Kebidanan dilaksanakan di ITB AAS Indonesia; Wonogiri hanya jejak penggabungan Akademi Kebidanan Giri Satria Husada ke ITB AAS pada 2024. Untuk jadwal/lokasi kelas Kebidanan dan Kampus 2, konfirmasi ke PMB/admin karena pemakaian ruang bisa berubah.","source":"https://itbaas.id/jalan-sehat-dalam-rangka-tasyakuran-keberhasilan-penyatuan-kampus-itb-aas-indonesia-dengan-akademi-kebidanan-giri-satria-husada-wonogiri/"},
]
rows=[]
removed=0
for line in open(path, encoding='utf-8'):
    if not line.strip(): continue
    obj=json.loads(line)
    if obj.get('q')==old_q:
        removed+=1; continue
    rows.append(obj)
for r in new_rows:
    if all(r['q']!=x.get('q') for x in rows): rows.append(r)
with open(path,'w',encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
print('removed', removed, 'total', len(rows))
