#!/bin/bash
# Planche contact. Le meilleur rapport bénéfice/effort de tout l'outillage.
# Employé 4 fois : 15 photos de réparation, 15 de démontage, 9 pages de
# schémas, 13 pages de service manual. À chaque fois : une planche, un regard,
# deux images retenues.
S=/tmp/.../scratchpad

# ---------- variante A : un dossier d'images
.venv/bin/python - <<'PY'
from PIL import Image, ImageDraw
import glob, os
S = "/tmp/.../scratchpad"
fs = sorted(glob.glob(S + "/mcv/*.jpeg"))
cols, cw, ch = 4, 560, 340
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols*cw, rows*ch), "white")
d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    im = Image.open(f); im.thumbnail((cw-8, ch-28))
    x, y = (i % cols)*cw, (i // cols)*ch
    sheet.paste(im, (x+4, y+24))
    d.text((x+6, y+6), os.path.basename(f), fill="black")   # <- non négociable
sheet.save(S + "/sheet-mcv.png")
print(sheet.size, len(fs))
PY

# ---------- variante B : les pages d'un PDF
# C'est ce qui a permis de repérer d'un coup d'œil la page « Power » dans un
# service manual de 24 pages, à son cartouche.
.venv/bin/python - <<'PY'
import pypdfium2 as p
from PIL import Image, ImageDraw
d = p.PdfDocument("/tmp/.../scratchpad/sm/emx1.pdf")
cols, cw, ch = 3, 640, 470
pages = list(range(1, 10))
rows = (len(pages) + cols - 1) // cols
sheet = Image.new("RGB", (cols*cw, rows*ch), "white")
dr = ImageDraw.Draw(sheet)
for k, i in enumerate(pages):
    im = d[i].render(scale=2).to_pil()     # scale=2 suffit pour trier
    im.thumbnail((cw-8, ch-26))
    x, y = (k % cols)*cw, (k // cols)*ch
    sheet.paste(im, (x+4, y+22))
    dr.text((x+6, y+5), f"page {i+1}", fill="black")
sheet.save("/tmp/.../scratchpad/sheet-emx1.png")
print(sheet.size)
PY

# Le nom de fichier / numéro de page écrit sur chaque vignette est essentiel :
# sans lui on voit l'image intéressante sans savoir laquelle c'est.
# Viser ~2000 px de large : au-delà, redimensionné à la lecture, illisible.
