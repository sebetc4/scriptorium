#!/bin/bash
# Galerie Imgur. La page d'album est montée en JavaScript : le HTML statique
# fait 7 Ko et ne cite qu'UNE image. L'API publique rend les 15.
# Sans ça, toute la galerie de réparation était perdue.
S=/tmp/.../scratchpad
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

for a in 0C2Nj zEsqp; do
  echo "== album $a"
  timeout 45 curl -s --max-time 40 -A "$UA" -H "Accept: application/json" \
    "https://api.imgur.com/post/v1/albums/$a?client_id=546c25a59c58ad7&include=media" \
    -o $S/alb-$a.json -w "http=%{http_code} size=%{size_download}\n"
  python3 -c "
import json
d = json.load(open('$S/alb-$a.json'))
print('title:', d.get('title'))
for m in d.get('media', []):
    print(' ', m.get('id'), m.get('ext'), m.get('width'), 'x', m.get('height'))
"
done

# Le client_id est celui du client web public d'Imgur : il peut cesser de
# fonctionner. Prévoir un message clair plutôt qu'un plantage.

# PIÈGE DE LA VIGNETTE : les pages de forum ne citent que
#   https://i.imgur.com/<id>h.jpg   -> miniature, 40 Ko, illisible
# l'original est
#   https://i.imgur.com/<id>.jpg    (ou .jpeg)   -> 1 à 3 Mo
# Retirer le `h` final. C'est ce qui sépare l'inexploitable du lisible.
grep -ohE 'https?://i\.imgur\.com/[A-Za-z0-9]+\.(jpg|png|jpeg)' $S/threads/t94641-full.html \
  | sort -u
