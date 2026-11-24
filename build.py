#!/usr/bin/env python3
"""Build the Vercel app (index.html) from the Claude artifact source.

The artifact page (artifact/workout-focus.html) is the source of truth. It is
written for the claude.ai viewer, which adds the <html>/<head> skeleton and the
synced database. This script wraps it as a standalone PWA page, stores data on
the device (localStorage) and pre-fills it from seed.json on first launch.

Usage: python3 build.py
"""
import json, pathlib, re

root = pathlib.Path(__file__).parent
src = (root / 'artifact' / 'workout-focus.html').read_text()
seed = json.loads((root / 'seed.json').read_text())

def sub(old, new):
    global src
    assert src.count(old) == 1, f'pattern not found once: {old[:60]}'
    src = src.replace(old, new)

# 1. the artifact viewer adds these; the standalone page needs its own
sub('<title>Workout Focus</title>\n<meta name="claude:viewport-fit-sides" content="cover">', '')
sub(':root{\n  color-scheme:dark;', ':root{\n  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);\n  color-scheme:dark;')

# 2. first launch on a device starts from the seed (week 1 from the "Wyniki" sheet)
sub("const persist = () => { try { localStorage.setItem(SKEY, JSON.stringify(store)); } catch(e){} };",
    "const persist = () => { try { localStorage.setItem(SKEY, JSON.stringify(store)); } catch(e){} };\n"
    "const SEED_INIT = " + json.dumps({'week': seed['week'], 'res': seed['res']}, ensure_ascii=False) + ";\n"
    "if (!Object.keys(store.res).length && !store.history.length) { store.week = SEED_INIT.week; store.res = JSON.parse(JSON.stringify(SEED_INIT.res)); persist(); }")

# 3. wording: data lives on this device
sub("local:'zapisano w tej przeglądarce'", "local:'zapisano na tym urządzeniu'")

# 4. offline support
sub("render();\nconnect();", "render();\nconnect();\nif ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});")

head = '''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Workout">
<meta name="theme-color" content="#0a0a0f">
<title>Workout Focus</title>
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon.png">
</head>
<body>
'''
(root / 'index.html').write_text(head + src.strip() + '\n</body>\n</html>\n')
print('index.html written')
