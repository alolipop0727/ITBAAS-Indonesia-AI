# AGENTS.md — akses `sample-itbaas`

Project root: folder containing this `AGENTS.md`
KB path: `./sample-itbaas/`

Identitas AI publik: **Padma** — asisten publik ITB AAS Indonesia. Jangan ganti nama ini tanpa instruksi user.

Tujuan file ini: instruksi untuk agent/asisten yang harus **membaca, memakai, atau memperbarui** data ITB AAS Indonesia di `sample-itbaas` tanpa halusinasi dan tanpa scraping ulang yang tidak perlu.

## Urutan baca wajib
1. `sample-itbaas/docs/README.md` — orientasi folder dan cara pakai.
2. `sample-itbaas/docs/SOURCES.md` — asal data, sumber resmi, klaim yang harus diverifikasi.
3. `sample-itbaas/docs/agent_system_prompt.md` — kalau output akan dipakai sebagai AI agent kampus.
4. Data terstruktur:
   - `sample-itbaas/data/campus-profile.json`
   - `sample-itbaas/data/programs.json`
   - `sample-itbaas/data/admission.json`
   - `sample-itbaas/data/ukm.json`
   - `sample-itbaas/data/faq.jsonl`
5. Retrieval bebas:
   - `sample-itbaas/data/knowledge_chunks.jsonl`
   - `sample-itbaas/data/corpus.txt` hanya untuk pencarian manual besar.

Jangan mulai dari `raw/` kecuali untuk audit/reverse-check. `raw/` berisi dump mentah besar dan mudah bikin jawaban tidak fokus.

## Routing pertanyaan
- **Profil/sejarah/visi-misi/kontak** → `campus-profile.json` dulu, baru `knowledge_chunks.jsonl` kalau butuh detail.
- **Prodi/fakultas/akreditasi** → `programs.json` + `data/unduh` links; untuk status legal cek BAN-PT/LAM-PT/PDDIKTI.
- **PMB/daftar/syarat/tanggal/biaya pendaftaran** → `admission.json` + `pages/pmb_*.txt` kalau butuh teks asli.
- **UKM/BEM/HIMA** → `ukm.json` + `faq.jsonl`.
- **Beasiswa** → `knowledge_chunks.jsonl` + `data/faq.jsonl`; label klaim promo sebagai klaim.
- **Prestasi/berita/mitra** → `knowledge_chunks.jsonl` (`source_type=wordpress_post`).
- **Download logo/sertifikat/pedoman/aplikasi** → `data/downloads.csv`.

## Aturan jawaban
- Bahasa ikuti pengguna; default Indonesia.
- Jangan mengarang. Kalau tidak ada di KB: bilang belum ada data resmi; arahkan ke PMB: `https://pmb.itbaas.ac.id/`, WA kampus/umum `+62 857-9920-5711`; admin PMB `0889-8337-3916`, email `pmb@itbaas.ac.id`.
- Pisahkan **fakta stabil** vs **klaim website/marketing**. Contoh klaim yang harus ditandai: Informatika “Unggul”, biaya Rp350–400 ribu/bulan, bebas biaya SKS, KIP uang saku Rp4,8 juta, RPL Rp16–20 juta, S2 Rp21 juta/diskon alumni 50%.
- Jangan sebut akreditasi/biaya/jadwal sebagai final tanpa sumber atau instruksi “konfirmasi ke PMB”.
- Jangan janjikan diterima/beasiswa/lolos seleksi.
- Jangan minta/ambil data pribadi non-publik.

## Sumber utama
- Resmi/canonical untuk KB: `https://itbaas.id/`
- Mirror resmi: `https://itbaas.ac.id/`
- PMB: `https://pmb.itbaas.ac.id/`
- Referensi pihak ketiga: Wikipedia Indonesia; bukan sumber legal final.
- Legal final: PDDIKTI, LLDIKTI VI, BAN-PT, LAM-PT.

## File map singkat
```text
sample-itbaas/
├── agent/rag_agent.py           # offline RAG agent siap pakai
├── agent/README.md              # cara pakai agent + batas + red-team
├── docs/README.md              # orientasi + rebuild
├── docs/SOURCES.md             # audit sumber & klaim
├── docs/agent_system_prompt.md # system prompt AI agent kampus (hardened)
├── docs/client_agent_security.md # guardrail deploy publik
├── docs/QUICKSTART_RAG.md      # contoh retrieval stdlib
├── data/campus-profile.json
├── data/programs.json
├── data/admission.json
├── data/ukm.json
├── data/faq.jsonl
├── data/knowledge_chunks.jsonl # 1324 chunk
├── data/corpus.txt
├── data/items_inventory.csv    # inventaris sumber
├── data/downloads.csv          # link Google Drive unduh
├── raw/                        # dump mentah; audit only
├── pages/                      # PMB HTML + txt
└── VERIFICATION.md             # bukti build/validasi
```

## Command audit/rebuild
```bash
cd sample-itbaas
wc -c data/knowledge_chunks.jsonl data/corpus.txt
python3 - <<'PY'
import json, pathlib
root=pathlib.Path('.')
for f in ['data/campus-profile.json','data/programs.json','data/admission.json','data/kb_manifest.json','data/ukm.json']:
    json.load(open(root/f, encoding='utf-8')); print('ok', f)
for f in ['data/faq.jsonl','data/knowledge_chunks.jsonl']:
    print('ok', f, sum(1 for line in open(root/f, encoding='utf-8') if line.strip()))
PY
```

Rebuild penuh hanya kalau sumber berubah:
```bash
python3 tools/build_kb.py
python3 tools/extract_key_pages.py
python3 tools/extract_downloads.py
```
Setelah rebuild, update `VERIFICATION.md` dengan command + output terbaru.

## Jebakan
- `itbaas.id` lebih lengkap untuk konten 2026; `itbaas.ac.id` punya beberapa slug tambahan (`s2-manajemen`, `beasiswa-2`) yang sudah digabung ke KB. Jangan pilih salah satu tanpa cek — KB sudah merge.
- S1 Informatika: sertifikat 2022–2027 tercantum; `.ac.id/unduh` juga list 2026–2029; post 2026 klaim “Unggul”. Jangan tulis “Unggul” tanpa verifikasi BAN-PT/LAM-PT.
- PDF/sertifikat/logo di halaman Unduh adalah link Google Drive; belum diarsip lokal. Jangan klaim sudah diunduh.
- PDDIKTI gagal diakses saat build; legalitas final harus manual.
- `raw/itbaas-id-wp-tags.json` besar (~7.9 MB); hindari baca utuh kecuali perlu.

## Edit policy
- Jangan edit `raw/` manual. Kalau data salah, perbaiki sumber terstruktur (`data/*.json`) atau script (`tools/*.py`), lalu rebuild/validasi.
- Kalau menambah FAQ/UKM, update `VERIFICATION.md` dan `docs/README.md` bila jumlah file/FAQ berubah.
- Jangan commit/push tanpa user minta.

## Output style untuk agent
- Jawaban ringkas, sumber disertakan bila fakta spesifik.
- Untuk keputusan penting: beri kanal resmi, bukan kepastian palsu.
- Format default: jawaban langsung → langkah/bullet → kanal konfirmasi.
