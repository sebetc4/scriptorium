#!/bin/bash
# Rendre et recadrer une page de PDF pour la lire. Employé 6 fois.
# Procédure : scale=2 pour TROUVER la page (planche contact, script 07),
#             scale=6 + recadrage pour LA LIRE.
S=/tmp/.../scratchpad

# ---------- rendu haute résolution + recadrage d'un schéma A3
.venv/bin/python - <<'PY'
import pypdfium2 as p
S = "/tmp/.../scratchpad"
d = p.PdfDocument(S + "/sm/emx1.pdf")
im = d[3].render(scale=6).to_pil()      # ~7146 x 5052 px
print(im.size)
im.save(S + "/emx1-power-full.png")
w, h = im.size
im.crop((int(w*0.02), int(h*0.35), int(w*0.42), int(h*0.95))).save(S + "/emx1-power-left.png")
PY
# scale=6 rend lisibles les valeurs de composants et les repères sur un A3.
# C'est ce qui a permis de lire « F1 / CPH6302 », « IC20 / S-8520 », le brochage
# S/G/D, et le contact de coupure du jack DJ1 du microKORG.

# ---------- recadrer une seconde fois dans le rendu déjà fait
.venv/bin/python - <<'PY'
from PIL import Image
S = "/tmp/.../scratchpad"
im = Image.open(S + "/emx1-power-full.png")
w, h = im.size
im.crop((int(w*0.34), int(h*0.48), int(w*0.72), int(h*0.80))).save(S + "/emx1-f1.png")
PY

# ---------- PIÈGE : NE PAS FAIRE CONFIANCE À L'EXTRACTION DE TABLEAUX.
# Le tableau de caractéristiques du CPH6302 est sorti colonnes entrelacées :
#
#   CV utoff Voltage GS(off) VDS=–10V, I D=0 –1mA –5 1. –V 2.
#
# Rendu en image, la même ligne se lit sans effort : V_GS(off), conditions,
# min −1,0, max −2,5, unité V.
# Sur un tableau de fiche technique : RENDRE ET LIRE L'IMAGE.
# L'extraction textuelle ne sert qu'à LOCALISER la page.
.venv/bin/python - <<'PY'
import pypdfium2 as p
S = "/tmp/.../scratchpad"
d = p.PdfDocument(S + "/cph6302.pdf")
d[0].render(scale=3).to_pil().save(S + "/cph-p1.png")
print("ok")
PY
