#!/bin/bash
# Recadrage fractionnaire + agrandissement. Employé ~8 fois.
# C'est ce qui a permis de lire DT2, DT37, C188, J4 sur les sérigraphies de PCB,
# de déchiffrer un schéma manuscrit, et de trancher trois désignations
# contradictoires données par les sources écrites.

# Coordonnées EN FRACTIONS, jamais en pixels : on vise sans connaître les
# dimensions de l'image.
# LANCZOS à l'agrandissement : sur du texte sérigraphié de 0,5 mm, l'écart avec
# le rééchantillonnage par défaut décide entre « lisible » et « pas lisible ».

.venv/bin/python - <<'PY'
from PIL import Image
S = "/tmp/.../scratchpad"

# --- zone d'alimentation sur une photo de PCB de 5312 x 2988
im = Image.open(S + "/mcv/VjoMIRY.jpeg")
w, h = im.size
print(im.size)
im.crop((int(w*0.05), int(h*0.15), int(w*0.62), int(h*0.85))) \
  .resize((1500, int(1500*(h*0.70)/(w*0.57)))) \
  .save(S + "/vjo-crop.png")
PY

# --- lire une étiquette précise sur un schéma manuscrit (C186 ou C188 ?)
.venv/bin/python - <<'PY'
from PIL import Image
S = "/tmp/.../scratchpad"
im = Image.open(S + "/imgs/schema-WwbyM8Y.jpeg")
w, h = im.size
im.crop((int(w*0.38), int(h*0.15), int(w*0.60), int(h*0.42))) \
  .resize((900, int(900*(h*0.27)/(w*0.22)))) \
  .save(S + "/sch-c186.png")
PY
