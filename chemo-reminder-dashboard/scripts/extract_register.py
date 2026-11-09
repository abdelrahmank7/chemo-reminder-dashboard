#!/usr/bin/env python3
"""Pull the register (data JSON) out of a saved dashboard HTML, so edits saved by the
pharmacist in the page become the basis for the next change.

Usage: python scripts/extract_register.py saved_index.html register.json [--summary]
"""
import json, re, sys
html = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'<script id="data"[^>]*>(.*?)</script>', html, re.S)
if not m: sys.exit('No data block found')
reg = json.loads(m.group(1)); json.dump(reg, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if '--summary' in sys.argv:
    print('rev', reg.get('rev'), 'saved', reg.get('savedAt'))
    for p in reg['patients']:
        v = (p.get('verification') or {}).get('first')
        print(p['code'], p.get('name'), 'MRN', p.get('mrn') or '-', 'BSA', p.get('bsa'), 'status', p.get('status'), 'confirmed' if v else 'awaiting approval', len(p.get('events') or []), 'events')
    print('last audit entries:'); [print(' ', a['at'], a.get('patient'), a['text'][:140]) for a in reg['audit'][-15:]]
