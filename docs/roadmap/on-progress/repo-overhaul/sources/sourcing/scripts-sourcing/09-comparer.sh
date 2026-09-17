#!/bin/bash
# Composite côte à côte, pour trancher une contradiction.
# Employé une fois, décisif : trois orthographes circulaient dans les sources
# écrites (DT2 / DP2 / D2). Deux photos de la même zone de carte, par deux
# personnes, sur deux machines différentes, recadrées au même endroit et
# normalisées à la même taille : la sérigraphie tranche.

.venv/bin/python - <<'PY'
from PIL import Image
S = "/tmp/.../scratchpad"
D = "/code/.../sources/images"

a = Image.open(S + "/auxren/IMG_9303.jpg"); w, h = a.size
ca = a.crop((int(w*0.05), int(h*0.50), int(w*0.24), int(h*0.78))).resize((760, 1120), Image.LANCZOS)

b = Image.open(D + "/j4-bridge-reference.png"); w, h = b.size
cb = b.crop((int(w*0.12), int(h*0.22), int(w*0.40), int(h*0.62))).resize((760, 1120), Image.LANCZOS)

out = Image.new("RGB", (1540, 1120), "white")
out.paste(ca, (0, 0)); out.paste(cb, (780, 0))
out.save(S + "/cmp-dt37.png")
print("ok — gauche: Auxren (E2, 2015) | droite: ancientcomputing")
PY

# Les deux recadrages sont normalisés à la MÊME taille de sortie (760x1120),
# sinon la comparaison est faussée par l'échelle.
