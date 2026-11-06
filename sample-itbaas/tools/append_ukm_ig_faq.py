#!/usr/bin/env python3
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = [
  {"q":"Lebih baik cek IG UKM atau DM UKM?","a":"Lebih baik dua-duanya: kepoin IG resmi UKM dulu untuk info terbaru (jadwal rekrutmen, kegiatan, dokumentasi). Kalau butuh jawaban spesifik, DM dengan sopan: perkenalkan diri, prodi/angkatan, niat gabung, tanya jadwal/syarat. Jangan spam DM atau berharap pasti dibalas; fallback ke PPKMB/Expo UKM atau WA kampus +62 857-9920-5711.","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
  {"q":"DM UKM isinya apa?","a":"Template singkat: halo Kak, saya <nama>, calon/mahasiswa ITB AAS prodi <prodi>. Mau tanya cara gabung <nama UKM>, syarat, jadwal rekrutmen, dan kegiatan. Boleh dibantu? Terima kasih.","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
]
with open(ROOT/'data/faq.jsonl','a',encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
print('appended', len(rows))
