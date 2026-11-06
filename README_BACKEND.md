# Padma — ITB AAS AI Backend (Express + Vercel)

**Padma** adalah asisten publik ITB AAS Indonesia. Backend publik memakai ASCND OpenAI-compatible API sebagai LLM, KB publik dari `sample-itbaas/` sebagai grounding. Key hanya di server env; tidak pernah dikirim ke client.

## Endpoints
- `GET /api/health` — cek service, model, KB loaded, configured flag
- `GET /api/chat?message=berapa biaya pendaftaran?` — test dari browser/curl
- `POST /api/chat` — body `{ "message": "berapa biaya pendaftaran?" }` → `{ ok, answer, sources, confidence, ... }`

## Local
```bash
npm install
cp .env.example .env   # isi ASCND_API_KEY asli
npm run dev
curl http://localhost:3100/api/health
curl 'http://localhost:3100/api/chat?message=berapa%20biaya%20pendaftaran?'
curl -X POST http://localhost:3100/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"berapa biaya pendaftaran?"}'
```

## Vercel deploy
1. Import repo `alolipop0727/ITBAAS-Indonesia-AI` di Vercel (root `/`, framework Other).
2. Set Environment Variables:
   - `ASCND_API_KEY` = key asli (jangan commit)
   - `ASCND_BASE_URL` = `https://api.ascnd.my.id/v1`
   - `ASCND_MODEL` = `deepseek-v4-flash-0731`
3. Deploy. `vercel.json` rewrite `/api/(.*)` → `/api/index.js`.
4. Test: `https://<project>.vercel.app/api/health`

## Security rules
- `ASCND_API_KEY` hanya server-side; client tidak pernah lihat.
- Public endpoint rate-limited (`RATE_MAX` / `RATE_WINDOW_MS`).
- CORS saat ini `*` (allow all) untuk test/demo; kalau production publik, ganti ke allowlist domain frontend.
- Request >800 chars ditolak; prompt injection/internal request ditolak sebelum API.
- Output di-scan: key patterns, system prompt echo, `.env`, stack paths → diganti fallback.
- Tidak ada akses ke SIAKAD/PMB/PDDIKTI; bukan layanan administratif resmi.
- Untuk keputusan daftar/bayar/akreditasi, agent selalu arahkan ke PMB/admin resmi.

## Notes
- `sample-itbaas/` ikut di-bundle supaya Vercel serverless bisa baca KB dari filesystem.
- `raw/` tidak dipakai runtime; jangan buka dari client.
- Untuk skala besar: ganti in-memory rate limit ke Upstash/Redis; tambahkan auth kalau endpoint jadi private.
