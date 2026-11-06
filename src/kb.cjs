// Public ITB AAS knowledge base loader + tiny BM25 retriever. No network, no secrets.
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DATA = path.join(ROOT, 'sample-itbaas', 'data');
const OFFICIAL = 'PMB: https://pmb.itbaas.ac.id/ | WA admin PMB 0889-8337-3916 | WA kampus/umum +62 857-9920-5711 | email pmb@itbaas.ac.id | telp (0271) 726156';

const STOP = new Set('yang dan di ke dari untuk dengan pada adalah itu ini atau dan nya saya anda kami kita mau tolong dong gimana apa saja berapa'.split(' '));
const BLOCK = ['system prompt','ignore previous','jailbreak','developer mode','.env','api key','password','token','raw/','internal','bocor','dump','credential','admin override','bypass'];

function readJson(name) { return JSON.parse(fs.readFileSync(path.join(DATA, name), 'utf8')); }
function readJsonl(name) { return fs.readFileSync(path.join(DATA, name), 'utf8').split(/\r?\n/).filter(Boolean).map(JSON.parse); }

const PROFILE = readJson('campus-profile.json');
const PROGRAMS = readJson('programs.json');
const ADMISSION = readJson('admission.json');
const UKM = readJson('ukm.json');
const FAQ = readJsonl('faq.jsonl');
const CHUNKS = readJsonl('knowledge_chunks.jsonl');

function tokenize(text) {
  return String(text || '').toLowerCase().match(/[a-z0-9]{2,}/g)?.filter(t => !STOP.has(t)) || [];
}

const DOCS = CHUNKS.map(c => tokenize(`${c.title || ''} ${c.text || ''}`));
const DF = new Map();
for (const doc of DOCS) for (const t of new Set(doc)) DF.set(t, (DF.get(t) || 0) + 1);
const N = DOCS.length;
const AVG = DOCS.reduce((a, d) => a + d.length, 0) / Math.max(N, 1);
const K1 = 1.4, B = 0.72;

function bm25(query, top = 6) {
  const q = tokenize(query);
  const scores = [];
  for (let i = 0; i < DOCS.length; i++) {
    const doc = DOCS[i];
    const tf = new Map();
    for (const t of doc) tf.set(t, (tf.get(t) || 0) + 1);
    let score = 0;
    for (const t of q) {
      if (!tf.has(t)) continue;
      const df = DF.get(t) || 0;
      const idf = Math.log((N - df + 0.5) / (df + 0.5) + 1);
      const f = tf.get(t);
      score += idf * (f * (K1 + 1)) / (f + K1 * (1 - B + B * doc.length / AVG));
    }
    if (score > 0) scores.push({ score, chunk: CHUNKS[i] });
  }
  scores.sort((a, b) => b.score - a.score);
  return scores.slice(0, top);
}

function faqMatch(query) {
  const q = new Set(tokenize(query));
  let best = { score: 0, faq: null };
  for (const f of FAQ) {
    const fq = new Set(tokenize(f.q));
    if (!fq.size) continue;
    const inter = [...q].filter(x => fq.has(x)).length;
    const union = new Set([...q, ...fq]).size;
    const score = inter / Math.max(union, 1);
    if (score > best.score) best = { score, faq: f };
  }
  return best;
}

function blocked(query) {
  const q = String(query || '').toLowerCase();
  return BLOCK.some(p => q.includes(p));
}

function officialAddress() {
  const ids = PROFILE.identity;
  const lines = [`Kampus 1: ${ids.address}`];
  for (const c of ids.campuses || []) {
    if (c.name === 'Kampus 2') lines.push(`Kampus 2: ${c.address}`);
  }
  lines.push(OFFICIAL);
  return lines.join('\n');
}

function officialContacts() {
  const c = PROFILE.contacts;
  const ids = PROFILE.identity;
  return [
    `Alamat: ${ids.address}`,
    `Telp: ${ids.phone}`,
    `WA kampus/umum: ${c.general_whatsapp} | WA admin PMB: ${c.pmb_whatsapp_admin}`,
    `Email: ${c.email_general} | ${c.email_info} | ${c.email_pmb}`,
    OFFICIAL,
  ].join('\n');
}

function programList() {
  return PROGRAMS.map(p => `- ${p.level} ${p.name} — ${p.faculty} (PMB id ${p.pmb_id})`).join('\n');
}

function ukmList() {
  return UKM.organizations.map(o => `- ${o.name}: ${o.focus} (${o.instagram})`).join('\n');
}

function directAnswer(query) {
  const q = String(query || '').toLowerCase();
  if (/\b(alamat|lokasi|kampus 1|kampus 2)\b/.test(q)) return { answer: officialAddress(), sources: ['data/campus-profile.json'], confidence: 'direct' };
  if (/\b(wa|whatsapp|nomor|kontak|telp|telepon|email)\b/.test(q)) return { answer: officialContacts(), sources: ['data/campus-profile.json'], confidence: 'direct' };
  if (/\b(program studi|prodi|jurusan|fakultas)\b/.test(q)) return { answer: programList(), sources: ['data/programs.json'], confidence: 'direct' };
  if (/\b(ukm|hima|bem)\b/.test(q)) return { answer: ukmList(), sources: ['data/ukm.json'], confidence: 'direct' };
  if (q.includes('biaya pendaftaran') || q.includes('daftar bayar')) {
    return { answer: `Biaya pendaftaran Rp${Number(ADMISSION.registration_fee_idr).toLocaleString('id-ID')} (transfer/tunai). Jalur KIP-K tercantum GRATIS di PMB; jalur lain berbayar. Biaya kuliah bisa berubah—konfirmasi ke PMB.\n${OFFICIAL}`, sources: ['data/admission.json', 'https://pmb.itbaas.ac.id/jalur-seleksi'], confidence: 'direct' };
  }
  return null;
}

function buildContext(query, top = 6) {
  const hits = bm25(query, top);
  const f = faqMatch(query);
  const parts = [];
  if (f.faq && f.score >= 0.30) {
    parts.push(`FAQ match (${f.score.toFixed(2)}): Q: ${f.faq.q}\nA: ${f.faq.a}\nsource: ${f.faq.source}`);
  }
  for (const h of hits) {
    const c = h.chunk;
    parts.push(`KB chunk score=${h.score.toFixed(2)} title=${c.title} url=${c.url}\n${String(c.text || '').slice(0, 1200)}`);
  }
  return { context: parts.join('\n\n'), sources: [...new Set([f.faq?.source, ...hits.map(h => h.chunk.url)].filter(Boolean))], hits };
}

function refusal() {
  return {
    answer: 'Bagian itu bukan informasi publik yang bisa saya berikan. Saya bisa bantu info publik ITB AAS: PMB, prodi, biaya resmi yang tercantum, kontak, UKM. Untuk urusan administratif/internal, hubungi PMB/admin resmi.',
    sources: [],
    confidence: 'blocked',
  };
}

module.exports = {
  PROFILE, PROGRAMS, ADMISSION, UKM, FAQ, CHUNKS,
  bm25, faqMatch, blocked, directAnswer, buildContext, refusal, OFFICIAL,
  kb: { chunks: CHUNKS.length, faq: FAQ.length, programs: PROGRAMS.length, ukm: UKM.organizations.length },
};
