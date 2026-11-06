#!/usr/bin/env python3
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
repls = {
    'AGENTS.md': [("WA `+62 857-9920-5711` / `0889-8337-3916`", "WA kampus/umum `+62 857-9920-5711`; admin PMB `0889-8337-3916`")],
    'sample-itbaas/agent/rag_agent.py': [
        ("OFFICIAL = 'PMB: https://pmb.itbaas.ac.id/ | WA +62 857-9920-5711 / 0889-8337-3916 | email pmb@itbaas.ac.id | telp (0271) 726156'",
         "OFFICIAL = 'PMB: https://pmb.itbaas.ac.id/ | WA admin PMB 0889-8337-3916 | WA kampus/umum +62 857-9920-5711 | email pmb@itbaas.ac.id | telp (0271) 726156'"),
    ],
    'sample-itbaas/docs/client_agent_security.md': [
        ("WA `+62 857-9920-5711` / `0889-8337-3916`.", "WA admin PMB `0889-8337-3916`; WA kampus/umum `+62 857-9920-5711`."),
    ],
    'sample-itbaas/docs/agent_system_prompt.md': [
        ("WA `+62 857-9920-5711` / `0889-8337-3916` · email", "WA admin PMB `0889-8337-3916`; WA kampus/umum `+62 857-9920-5711` · email"),
        ("- Telp: `(0271) 726156` · WA umum/PMB: `+62 857-9920-5711` · admin PMB: `0889-8337-3916`",
         "- Telp: `(0271) 726156` · WA kampus/umum: `+62 857-9920-5711` · WA admin PMB: `0889-8337-3916`"),
    ],
    'sample-itbaas/docs/SOURCES.md': [
        ("- Telepon: (0271) 726156; WA: 0857-9920-5711 / 0889-8337-3916 (PMB)",
         "- Telepon: (0271) 726156; WA kampus/umum: 0857-9920-5711; WA admin PMB: 0889-8337-3916"),
        ("PMB `pmb@itbaas.ac.id`, WA `+62 857-9920-5711`, telp `(0271) 726156`.",
         "PMB `pmb@itbaas.ac.id`, WA admin PMB `0889-8337-3916`, telp `(0271) 726156`."),
    ],
    'sample-itbaas/data/faq.jsonl': [
        ("WA +62 857-9920-5711 / 0889-8337-3916", "WA kampus/umum +62 857-9920-5711; WA admin PMB 0889-8337-3916"),
    ],
}
for rel, pairs in repls.items():
    p = PROJECT/rel
    s = p.read_text(encoding='utf-8')
    orig = s
    for a,b in pairs: s = s.replace(a,b)
    if s != orig: p.write_text(s, encoding='utf-8'); print('patched', rel)
# JSON: rename ambiguous alt keys
for rel in ['sample-itbaas/data/campus-profile.json','sample-itbaas/data/admission.json']:
    p=PROJECT/rel; d=json.loads(p.read_text(encoding='utf-8'))
    changed=False
    def fix(obj):
        global changed
        if isinstance(obj, dict):
            if 'pmb_whatsapp_alt' in obj:
                obj['campus_whatsapp'] = obj.pop('pmb_whatsapp_alt'); changed=True
            for v in obj.values(): fix(v)
        elif isinstance(obj, list):
            for v in obj: fix(v)
    fix(d)
    if changed: p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8'); print('patched', rel)
