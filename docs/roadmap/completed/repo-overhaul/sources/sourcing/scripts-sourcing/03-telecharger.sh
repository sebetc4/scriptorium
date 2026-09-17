#!/bin/bash
# Récupération en lot. Deux règles apprises à la dure, toutes deux silencieuses
# quand on les oublie.
S=/tmp/.../scratchpad
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# RÈGLE 1 — chemins absolus. Le répertoire courant est réinitialisé entre deux
# appels d'outil : `cd $S && curl -o fichier &` écrit ailleurs, sans rien dire.
# Ça m'a coûté un lot entier de cinq fichiers.

# RÈGLE 2 — contrôler les tailles en lot. Trois fichiers de taille rigoureusement
# identique = trois pages d'erreur. C'est arrivé sur la pagination d'un fil
# archivé : t94641-p15/p30/p45 faisaient 4684 octets chacun.

# --- parallélisme par lots de 6 à 8 ; au-delà les serveurs jettent des connexions
mkdir -p $S/imgs
i=0
for id in 8MayZ1J 9Loq21v bT7oKli GrgUuSh L1OXqNn mRJj8ws n2pGVSM Sk3Px7Z UfluvSr YYacgBC; do
  i=$((i+1))
  timeout 60 curl -sL --max-time 55 -A "$UA" -o "$S/imgs/$id.jpg" "https://i.imgur.com/$id.jpg" &
  [ $((i % 6)) -eq 0 ] && wait
done
wait
for f in $S/imgs/*.jpg; do echo "$f $(stat -c%s $f) $(file -b --mime-type $f)"; done

# --- chaîne de replis sur miroirs : la fiche Sanyo a demandé quatre tentatives.
#     alldatasheet, datasheetq, datasheetbank, chipfind : tous 403.
#     Un miroir obscur a fini par la servir.
for u in "https://www.mouser.com/datasheet/2/308/CPH6302-D-1809982.pdf" \
         "https://www.onsemi.com/pub/Collateral/CPH6302-D.PDF" \
         "http://www.1688eric.com/upload/pdf/2012-10-16/CPH6302.pdf"; do
  echo "== $u"
  timeout 45 curl -sL --max-time 40 -A "$UA" -o $S/ds.tmp \
    -w "  http=%{http_code} mime=%{content_type} size=%{size_download}\n" "$u"
  m=$(file -b --mime-type $S/ds.tmp); echo "  $m"
  if [ "$m" = "application/pdf" ]; then cp $S/ds.tmp $S/cph6302.pdf; echo "  -> SAUVÉ"; break; fi
done
