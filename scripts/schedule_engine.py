#!/usr/bin/env python3
"""Daily reminder check on a dashboard register.

Lists clinic doses exactly LEAD days ahead (default 7, from settings.lead) for confirmed
patients, skipping ones already in sent_log, and flags doses inside the lead window that
never got a reminder. Mirrors the page's own rules.

Usage: python scripts/schedule_engine.py register.json --today YYYY-MM-DD [--lead 7]
"""
import argparse, json, sys
from datetime import date, timedelta
LIVE = {'scheduled', 'delayed'}
ap = argparse.ArgumentParser(); ap.add_argument('register'); ap.add_argument('--today', required=True); ap.add_argument('--lead', type=int)
a = ap.parse_args(); reg = json.load(open(a.register, encoding='utf-8'))
lead = a.lead or reg.get('settings', {}).get('lead', 7)
today = date.fromisoformat(a.today); target = today + timedelta(days=lead)
sent = {(s['eventId'], s['date']) for s in reg.get('sent_log', [])}
due, missed, held = [], [], []
for p in reg['patients']:
    confirmed = bool((p.get('verification') or {}).get('first'))
    for e in p.get('events') or []:
        if not e.get('remind') or e.get('state') not in LIVE: continue
        d = date.fromisoformat(e['date']); key = (e['id'], e['date'])
        row = {'patient': p.get('name') or p['code'], 'mrn': p.get('mrn') or 'Not recorded', 'drug': e['drug'], 'week': e.get('week'), 'date': e['date']}
        if key in sent or d < today: continue
        if d == target: (due if confirmed else held).append(row)
        elif d < target and (d - timedelta(days=lead)) < today: missed.append(row)
json.dump({'today': a.today, 'lead_days': lead, 'treatment_date': target.isoformat(), 'email_items': due,
           'held_awaiting_approval': held, 'missed_reminders': missed}, sys.stdout, indent=2, ensure_ascii=False); print()
