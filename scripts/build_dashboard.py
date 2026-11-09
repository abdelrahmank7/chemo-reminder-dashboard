#!/usr/bin/env python3
"""Assemble the self-contained dashboard HTML from the skill assets and a register JSON.

Usage:
  python scripts/build_dashboard.py --register register.json --out /mnt/user-data/outputs/index.html
  python scripts/build_dashboard.py --from-html saved_index.html --out ...   # rebuild a saved board with the current code

The register is the dashboard's data object (see references/data-model.md).
Patients may be given as `seedPhases` + `seedOps` instead of `events`; the page builds
the schedule from the templates on first load (see the "seed" section of data-model.md).
"""
import argparse, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, '..', 'assets')
def read(p): return open(p, encoding='utf-8').read()
def extract(html, i):
    m = re.search(r'<script id="%s"[^>]*>(.*?)</script>' % i, html, re.S); return m.group(1) if m else None
ap = argparse.ArgumentParser(); ap.add_argument('--register'); ap.add_argument('--from-html'); ap.add_argument('--out', required=True)
a = ap.parse_args()
if a.from_html:
    reg = json.loads(extract(read(a.from_html), 'data'))
elif a.register:
    reg = json.loads(read(a.register))
else:
    sys.exit('Give --register or --from-html')
if not reg.get('protocols'): reg['protocols'] = json.loads(read(os.path.join(A, 'protocols.json')))
reg.setdefault('settings', {}).setdefault('lead', 7); reg['settings'].setdefault('runway', 7); reg['settings'].setdefault('autoConfirmPast', True)
if 'demoSeed' not in reg: reg['demoSeed'] = json.loads(json.dumps(reg))
head = read(os.path.join(A, 'head.html')); css = read(os.path.join(A, 'style.css'))
app = read(os.path.join(A, 'app.js')).replace('__HEAD__', json.dumps(head))
refs = read(os.path.join(A, 'refs.json'))
assert '</script' not in app.lower()
data = json.dumps(reg, ensure_ascii=False).replace('<', '\\u003c')
html = ('<!doctype html>\n<html lang="en">\n<head>' + head + '<style id="css">' + css + '</style>\n</head>\n<body>\n'
        '<div id="root"></div><div id="modal"></div><div class="toasts" id="toasts" aria-live="polite"></div>\n'
        '<script id="data" type="application/json">' + data + '</script>\n'
        '<script id="refs" type="application/json">' + refs + '</script>\n'
        '<script id="app">' + app + '</script>\n</body>\n</html>\n')
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
open(a.out, 'w', encoding='utf-8').write(html)
print('wrote', a.out, len(html) // 1024, 'KB;', len(reg.get('patients', [])), 'patients')
