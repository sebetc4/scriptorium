#!/bin/bash
# Localiser un terme dans un ou plusieurs PDF, et détecter les pages scannées.
# Employé 4 fois. Quatre manuels, 79 pages, une seconde.
S=/tmp/.../scratchpad

# ---------- chercher un terme dans un lot de manuels
.venv/bin/python - <<'PY'
import pypdfium2 as p, glob, os
for f in sorted(glob.glob("/tmp/.../scratchpad/sm/*.pdf")):
    d = p.PdfDocument(f)
    hits = []
    for i in range(len(d)):
        t = d[i].get_textpage().get_text_range()
        if "CPH6302" in t or "CPH 6302" in t:
            hits.append(i+1)
    print(f"{os.path.basename(f):16s} {len(d):3d} pages — CPH6302 en page(s) : "
          f"{hits or 'aucune (texte non extractible ?)'}")
PY
# -> emx1: p22, microkorg: p12, em1: p12, ms2000: p23 et p26

# ---------- DÉTECTER LES PAGES SCANNÉES. Distinction essentielle.
# Les schémas des service manuals Korg rendent 0 caractère : purement
# graphiques. Un script qui ne fait qu'extraire du texte conclut « rien dans ce
# PDF » alors que l'essentiel y est.
.venv/bin/python - <<'PY'
import pypdfium2 as p
d = p.PdfDocument("/tmp/.../scratchpad/sm/emx1.pdf")
for i in range(1, 10):
    t = d[i].get_textpage().get_text_range()
    kws = [k for k in ("DC9V", "POWER", "BATT", "SW1", "FET", "+5V", "9V") if k in t.upper()]
    print(f"p{i+1}: {len(t):6d} car. | {kws}")
PY
# -> toutes à 0 caractère : len(texte) == 0 -> basculer en rendu d'image

# ---------- lire le contexte d'un terme dans une nomenclature
.venv/bin/python - <<'PY'
import pypdfium2 as p, re
for f, pg in (("emx1", 22), ("microkorg", 12), ("em1", 12)):
    d = p.PdfDocument(f"/tmp/.../scratchpad/sm/{f}.pdf")
    t = re.sub(r'[ \t]+', ' ', d[pg-1].get_textpage().get_text_range())
    i = t.find("CPH6302")
    print(f"\n===== {f}.pdf p{pg} =====")
    print(t[max(0, i-500):i+260])
PY
