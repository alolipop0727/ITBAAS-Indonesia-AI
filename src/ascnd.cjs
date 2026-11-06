// ASCND OpenAI-compatible client. Key is server-side env only; never exposed to client.
'use strict';

const BASE = (process.env.ASCND_BASE_URL || 'https://api.ascnd.my.id/v1').replace(/\/+$/, '');
const MODEL = process.env.ASCND_MODEL || 'deepseek-v4-flash-0731';
const TIMEOUT_MS = Number(process.env.ASCND_TIMEOUT_MS || 90000);

const FALLBACK = 'Saya belum punya jawaban resmi untuk itu. Konfirmasi ke PMB: https://pmb.itbaas.ac.id/ | WA admin PMB 0889-8337-3916 | WA kampus/umum +62 857-9920-5711.';

function outputDlp(text) {
  const t = String(text || '');
  const banned = [
    /sk-[A-Za-z0-9_-]{10,}/i,
    /ASCND_API_KEY/i,
    /system prompt/i,
    /developer message/i,
    /\.env\b/i,
    /raw\//i,
    /BEGIN (RSA|OPENSSH|PRIVATE) KEY/i,
    /stack trace/i,
    /\/var\/task\/[^\s]*/i,
    /\/home\/[^\s]*/i,
  ];
  return !banned.some(rx => rx.test(t));
}

async function chatCompletion(system, user, maxTokens = 700) {
  const key = process.env.ASCND_API_KEY;
  if (!key) return { ok: false, status: 503, error: 'AI backend not configured' };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${BASE}/chat/completions`, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: system },
          { role: 'user', content: user },
        ],
        temperature: 0.2,
        max_tokens: maxTokens,
      }),
    });
    const body = await res.text();
    if (!res.ok) return { ok: false, status: 502, error: 'AI upstream error', upstreamStatus: res.status };
    let data;
    try { data = JSON.parse(body); } catch { return { ok: false, status: 502, error: 'AI upstream bad json' }; }
    const content = data?.choices?.[0]?.message?.content || '';
    if (!content || !outputDlp(content)) return { ok: false, status: 200, answer: FALLBACK, confidence: 'fallback', usage: data?.usage || null };
    return { ok: true, answer: content.trim(), confidence: 'ai', usage: data?.usage || null, model: data?.model || MODEL };
  } catch (err) {
    const aborted = err && err.name === 'AbortError';
    return { ok: false, status: aborted ? 504 : 502, error: aborted ? 'AI upstream timeout' : 'AI upstream unreachable' };
  } finally {
    clearTimeout(timer);
  }
}

module.exports = { chatCompletion, FALLBACK, MODEL, BASE };
