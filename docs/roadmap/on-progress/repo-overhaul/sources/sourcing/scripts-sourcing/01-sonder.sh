#!/bin/bash
# Sonder une URL sans rien télécharger. Premier geste, systématiquement.
# Employé en continu tout au long de l'enquête.
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# --- forme employée pour établir que korgforums était entièrement HS
for u in "https://korgforums.com/forum/phpBB3/viewtopic.php?p=699929" \
         "https://www.korgforums.com/forum/phpBB3/" \
         "https://www.korgforums.com/" ; do
  echo "== $u"
  curl -sk -A "$UA" -o /dev/null \
    -w "http=%{http_code} size=%{size_download} eff=%{url_effective}\n" "$u"
done

# --- forme avec type MIME, employée sur les fiches techniques
# curl -sk -A "$UA" -o /dev/null \
#   -w "http=%{http_code} size=%{size_download} type=%{content_type}\n" URL

# --- vérification du contenu réellement reçu, après téléchargement.
#     Plusieurs .pdf ont répondu 200 avec du HTML.
# m=$(file -b --mime-type fichier.pdf)
# [ "$m" = "application/pdf" ] || echo "ce n'est pas un PDF : $m"
