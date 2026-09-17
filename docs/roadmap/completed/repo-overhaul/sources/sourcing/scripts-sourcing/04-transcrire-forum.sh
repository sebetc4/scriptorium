#!/bin/bash
# Mise en fiche verbatim d'un fil, avec en-tête de provenance.
# Employé deux fois : forme simple (phpBB via strip.py), forme à motifs
# (Audiofanzine, qui a demandé un repli).
S=/tmp/.../scratchpad
D=/code/claude/pdf-creator/library/electronique/repair/electribe-2/sources/threads

# ---------- forme 1 : phpBB. strip.py fait tout, on ajoute l'en-tête.
#            Le `sed -n '5,600p'` saute le bandeau du forum, constant.
save(){ # $1=slug  $2=titre  $3=url  $4=snapshot  $5=fichier html
cat > $D/$1.md <<EOF
---
titre: $2
url_origine: $3
archive: https://web.archive.org/web/$4
recupere_le: 2026-09-12
note: >
  Transcription texte de la page archivée. Le forum korgforums.com renvoyait
  HTTP 500 sur toutes ses pages au moment de la collecte ; la Wayback Machine
  est la seule voie d'accès. Texte non retouché, hors nettoyage du balisage.
---

EOF
cd $S && python3 strip.py threads/$5 | sed -n '5,600p' >> $D/$1.md
echo "$1.md $(wc -l < $D/$1.md) lignes"
}

save korgforums-t105619-service-manual "Electribe 2/Sampler service manual" \
  "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=105619" \
  "20251115085815/https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=105619&view=print" \
  t105619-print.html
# ... huit appels de ce type

# ---------- forme 2 : gabarit inconnu, avec repli de motif.
# PIÈGE : la première version, sans le repli, a écrit « 0 messages transcrits »
# et produit un fichier vide sans que rien ne signale l'échec.
cd $S && python3 - <<'PY'
import re, html
s = open('af638190.html', encoding='utf-8', errors='replace').read()
s = re.sub(r'(?is)<script.*?</script>', '', s)
s = re.sub(r'(?is)<style.*?</style>', '', s)

posts = re.findall(r'(?is)<div[^>]*class="[^"]*\bmessage\b[^"]*"[^>]*>(.*?)</div>\s*</div>', s)
if not posts:                                    # <- le repli qui manquait
    posts = re.findall(r'(?is)itemprop="text"[^>]*>(.*?)</div>', s)

out = ["---", "titre: \"Electribe 2 s'éteint toute seule ! (Sur secteur)\"",
       "url_origine: https://fr.audiofanzine.com/...",
       "recupere_le: 2026-09-12", "note: >",
       "  Fil francophone, 2017-2021. Site en ligne, récupéré directement.",
       "  Les pseudonymes ne sont pas restitués par l'extraction : les messages",
       "  sont donnés dans l'ordre du fil.", "---", "",
       "Messages dans l'ordre de publication.", ""]
n = 0
for p in posts:
    t = re.sub(r'(?i)<br\s*/?>', '\n', p)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(re.sub(r'[ \t]+', ' ', t)).strip()
    t = re.sub(r'\n{3,}', '\n\n', t)
    if len(t) > 40:
        n += 1
        out.append(f"### Message {n}\n\n{t}\n")
open("/code/.../threads/audiofanzine-638190.md", "w").write("\n".join(out))
print(n, "messages transcrits")
PY
