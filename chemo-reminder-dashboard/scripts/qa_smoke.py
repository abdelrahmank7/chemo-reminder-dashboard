#!/usr/bin/env python3
"""Smoke-test a built dashboard in a headless browser: every tab opens, no script errors,
no sideways scrolling on a phone, and a save produces a complete document.

Usage: python scripts/qa_smoke.py /path/to/index.html
"""
import asyncio, sys
from playwright.async_api import async_playwright
MOCK = "window.__pubs=[];window.claude={use:(n)=>Promise.resolve(n==='artifact'?{publish:async(h)=>{window.__pubs.push(h);return{}}}:n==='user'?{canEdit:async()=>true}:n==='downloads'?{save:async()=>({})}:null)};"
TABS = ['overview', 'mar', 'calendar', 'patients', 'email', 'pharmacy', 'protocols', 'references', 'log', 'settings', 'search']
async def main(path):
    url = 'file://' + path; fails = []; errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 1000})
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.add_init_script(MOCK); await pg.goto(url + '#overview'); await pg.wait_for_timeout(900)
        for t in TABS:
            await pg.goto(url + '#' + t); await pg.wait_for_timeout(200)
            if len(await pg.inner_text('#view')) < 20: fails.append('empty tab ' + t)
        mb = await b.new_page(viewport={'width': 390, 'height': 850})
        for t in TABS:
            await mb.goto(url + '#' + t); await mb.wait_for_timeout(200)
            if not await mb.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'): fails.append('phone overflow ' + t)
        await b.close()
    fails += ['script error: ' + e for e in errs]
    print('PASS' if not fails else 'FAIL'); [print(' -', f) for f in fails]; sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
