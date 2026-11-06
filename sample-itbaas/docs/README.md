# sample-itbaas — Knowledge Base ITB AAS Indonesia untuk AI Agent

Dibuat: 2026-11-06. Asumsi: data publik saja; tidak ada data autentikasi SIAKAD/PDDIKTI. `itbaas.id` dipakai sebagai sumber konten utama (lebih banyak post 2026), slug yang hanya ada di `itbaas.ac.id` ikut digabung. Klaim marketing dicatat sebagai klaim, bukan fakta final.

## Isi folder

```text
sample-itbaas/
├── raw/                         # dump mentah: sitemap XML + WP REST API JSON + Wikipedia HTML
├── pages/                       # halaman PMB (HTML + extracted .txt)
├── assets/                      # logo ITB AAS (3 file)
├── data/
│   ├── campus-profile.json      # profil institusi terstruktur
│   ├── programs.json            # 9 prodi: fakultas, PMB id, akreditasi, fokus
│   ├── admission.json           # PMB 2027 Ganjil: jalur, tanggal, syarat, alur
│   ├── faq.jsonl                # 80 tanya-jawab siap dipakai agent
│   ├── ukm.json                 # daftar BEM/HIMA/UKM + Instagram + aturan jawab
│   ├── knowledge_chunks.jsonl   # 1324 chunk RAG (id, source, url, title, text)
│   ├── corpus.txt               # semua chunk dalam format teks
│   ├── items_inventory.json/csv # inventaris 436 item sumber
│   ├── downloads.csv            # 17 link Unduh (logo/sertifikat/pedoman/aplikasi)
│   ├── kb_manifest.json         # ringkasan build
│   └── key-pages.txt            # ekstrak halaman kunci (profil/visi/sejarah/PMB/beasiswa)
├── agent/                       # offline RAG agent (stdlib; no keys/network)
├── docs/
│   ├── README.md                # file ini
│   ├── agent_system_prompt.md   # system prompt siap pakai (hardened)
│   ├── client_agent_security.md # guardrail deploy: input/RAG/tool/output/incident
│   ├── SOURCES.md               # daftar sumber + catatan verifikasi
│   └── QUICKSTART_RAG.md        # cara pakai JSONL untuk retrieval sederhana
└── tools/                       # script build/ekstraksi
```

## Angka hasil build
- Sumber: `itbaas.id`, `itbaas.ac.id`, `pmb.itbaas.ac.id`, `id.wikipedia.org`
- Items: 436 (WP pages+posts yang lolos strip HTML + PMB + Wikipedia)
- Chunks: 1324 (`data/knowledge_chunks.jsonl`)
- Total teks: ~1.33 juta karakter
- Raw dump: `raw/` (sitemap, posts/pages/categories/tags/media JSON; media hanya metadata, gambar tidak diunduh semua)

## Cara pakai untuk AI agent
1. Pakai `docs/agent_system_prompt.md` sebagai system prompt.
2. Coba offline agent: `python3 agent/rag_agent.py 'berapa biaya pendaftaran'`; lihat `agent/README.md`.
3. Baca `docs/client_agent_security.md` sebelum deploy publik (server-side enforcement, tool allowlist, DLP, logging).
4. Load `data/faq.jsonl` untuk jawaban cepat/intent matching; untuk pertanyaan UKM, baca `data/ukm.json`.
5. Untuk pertanyaan bebas, lakukan retrieval dari `data/knowledge_chunks.jsonl` (lihat `docs/QUICKSTART_RAG.md`).
6. Untuk fakta terstruktur (alamat, kontak, prodi, jalur PMB), baca `campus-profile.json`, `programs.json`, `admission.json` — jangan generatif dari memori model.
7. Untuk keputusan penting, agent wajib mengarahkan ke kanal resmi.

## Rebuild
```bash
python3 tools/build_kb.py
python3 tools/extract_key_pages.py
python3 tools/extract_downloads.py
```

## Verifikasi cepat
```bash
python3 - <<'PY'
import json, pathlib
root=pathlib.Path('.')
for f in ['data/campus-profile.json','data/programs.json','data/admission.json','data/kb_manifest.json','data/ukm.json']:
    json.load(open(root/f, encoding='utf-8')); print('ok', f)
n=sum(1 for _ in open(root/'data/faq.jsonl', encoding='utf-8')); print('faq', n)
n=sum(1 for _ in open(root/'data/knowledge_chunks.jsonl', encoding='utf-8')); print('chunks', n)
PY
```

## Batas & catatan
- PDDIKTI tidak bisa diakses saat pengumpulan; legalitas final cek `pddikti.kemdikbud.go.id` / LLDIKTI VI / BAN-PT / LAM-PT.
- `itbaas.id` vs `itbaas.ac.id`: konten hampir sama; `.id` lebih lengkap untuk 2026, `.ac.id` punya `s2-manajemen` dan `beasiswa-2` yang ikut digabung.
- Sertifikat S1 Informatika: `.id/unduh` list 2022–2027; `.ac.id/unduh` juga list 2026–2029; post 2026 klaim "Unggul". Jangan tulis "Unggul" tanpa verifikasi.
- Biaya kuliah/SPP/DPA/SKS dan beasiswa berubah; agent harus label "klaim website, konfirmasi PMB".
- Data pribadi mahasiswa/dosen tidak dikumpulkan; hanya konten publik.
