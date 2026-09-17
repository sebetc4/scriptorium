#!/bin/bash
# Wayback Machine. Le pilier : sans elle, aucune source primaire sur ce dossier.
# Employé une quinzaine de fois.
S=/tmp/.../scratchpad     # répertoire de travail, toujours en absolu

# --- 1. Disponibilité en lot, avant de télécharger quoi que ce soit.
#        Deux sujets sur douze n'avaient aucune capture : su en cinq secondes.
for t in 105619 117977 94641 122752 118602 120597 119219 122229 99129; do
  echo "--- t=$t"
  timeout 35 curl -s --max-time 30 \
    "http://web.archive.org/cdx/search/cdx?url=korgforums.com/forum/phpBB3/viewtopic.php%3Ft%3D$t*&fl=timestamp,original&filter=statuscode:200&collapse=urlkey&limit=20"
done

# --- 2. Même chose sur des permaliens de message. A renvoyé zéro sur les huit.
#        C'est ce constat qui a imposé la résolution p= -> t= de l'étape 4.
for p in 699929 699938 699924 696524 623720 623432 622428 791999; do
  r=$(timeout 30 curl -s --max-time 25 \
    "http://web.archive.org/cdx/search/cdx?url=korgforums.com/forum/phpBB3/viewtopic.php%3Fp%3D$p&matchType=exact&fl=timestamp,original,statuscode&limit=5&collapse=digest")
  echo "p=$p => ${r:-none}"
done

# --- 3. Récupération. Préférer la vue print : tout le fil sur une page propre.
#        16 Ko en print contre 91 Ko en vue normale, pour le même fil.
dl(){ timeout 90 curl -s --max-time 85 -L -o "$S/threads/$1" "https://web.archive.org/web/$2"
      echo "$1 $(stat -c%s $S/threads/$1 2>/dev/null)"; }

dl t105619-print.html "20251115085815/https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=105619&view=print" &
dl t94641-print.html  "20251123171429/https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641&view=print" &
# la vue normale en plus, quand le fil porte des images : la print perd les
# liens de pièces jointes
dl t94641-full.html   "20250827175934/http://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641" &
wait
ls -la $S/threads/

# --- 4. Résoudre p= -> t= : reconstruire l'index du sous-forum depuis ses
#        listings archivés. Site HS, donc pas de redirection à suivre.
timeout 45 curl -s --max-time 40 \
  "http://web.archive.org/cdx/search/cdx?url=korgforums.com/forum/phpBB3/viewforum.php*&fl=timestamp,original&filter=statuscode:200&collapse=urlkey&limit=2000" \
  | grep -E "f=48" > $S/f48.list
wc -l < $S/f48.list

mkdir -p $S/f48all
i=0
while read ts url; do
  i=$((i+1)); out="$S/f48all/$(printf %03d $i).html"
  [ -s "$out" ] || timeout 50 curl -s --max-time 45 -L -o "$out" "https://web.archive.org/web/$ts/$url" &
  [ $((i % 8)) -eq 0 ] && wait
done < $S/f48.list
wait

# la table titre -> identifiant de sujet
grep -ohE 'viewtopic\.php\?t=[0-9]+[^"]*" class="topictitle">[^<]*' $S/f48all/*.html \
  | sed 's/&amp;sid=[a-f0-9]*//; s/" class="topictitle">/ | /' | sort -u > $S/topics.txt
wc -l < $S/topics.txt
grep -iE "guts|service manual|schematic|power|repair|klm" $S/topics.txt
