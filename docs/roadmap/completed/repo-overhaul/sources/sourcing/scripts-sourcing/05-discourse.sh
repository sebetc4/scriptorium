#!/bin/bash
# Forum Discourse : l'endpoint .json plutôt que du grattage.
# Auteurs, dates, corps propre. Aucune regex fragile.
# A marché du premier coup là où les pages HTML du même site renvoyaient 403.
S=/tmp/.../scratchpad
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

timeout 45 curl -sL --max-time 40 -A "$UA" -H "Accept: application/json" \
  -o $S/syntaur.json -w "http=%{http_code} size=%{size_download}\n" \
  "https://forums.syntaur.com/t/korg-electribe-2-sampler-won-t-power-on/1499.json"

python3 - <<'PY'
import json, re, html
d = json.load(open("/tmp/.../scratchpad/syntaur.json"))
print('TITLE:', d.get('title'))
for p in d['post_stream']['posts']:
    t = re.sub(r'<[^>]+>', '', p['cooked'])
    t = html.unescape(re.sub(r'\s+', ' ', t)).strip()
    print('---', p['username'], p['created_at'][:10])
    print(t[:1500])
PY

# Reconnaître un Discourse : <meta name="generator" content="Discourse">,
# ou des URL en /t/<slug>/<id>. Vaut le coup à l'aveugle : ça coûte une requête.
