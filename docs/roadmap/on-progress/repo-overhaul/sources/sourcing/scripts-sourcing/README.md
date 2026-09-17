# Scripts de sourcing — tels qu'employés

> **Archive, remplacée le 2026-09-13** par les outils de la skill `sourcing`
> (`.claude/skills/sourcing/scripts/`), généralisés, testés, et qui échouent
> bruyamment. Ces scripts restent ici tels qu'ils ont tourné ; ne pas les
> exécuter ni les corriger.

Sortis bruts de l'enquête Electribe 2 (voir `../outillage-sourcing.md` pour
l'analyse et les leçons). **Rien n'a été nettoyé, généralisé ni paramétré** :
c'est l'état exact dans lequel ils ont tourné, avec leurs chemins en dur, leurs
tableaux de correspondance spécifiques et leurs raccourcis.

C'est voulu. L'intérêt de ces fichiers est de montrer ce qui a réellement été
exécuté et dans quel ordre, pas de fournir une bibliothèque. La phase
d'intégration décidera de ce qui devient une API propre.

## Deux formes

| Forme | Pourquoi |
|---|---|
| `.py` | fichiers qui existaient déjà comme tels, appelés plusieurs fois d'affilée |
| `.sh` | blocs exécutés en une passe via `.venv/bin/python - <<PY … PY` ou directement en bash — restitués avec leur enveloppe shell, parce que c'est elle qui portait les chemins et les boucles |

Les `.sh` contiennent la substitution `$S` → répertoire de travail temporaire,
telle qu'elle était faite au moment de l'exécution. Elle est en tête de chaque
fichier.

## Ordre réel d'utilisation

1. `01-sonder.sh` — établir ce qui répond avant toute chose
2. `02-wayback.sh` — trouver ce qui est archivé, résoudre `p=` → `t=`
3. `03-telecharger.sh` — récupération en lot, en parallèle
4. `strip.py` — HTML → texte, appelé après chaque récupération
5. `04-transcrire-forum.sh` — mise en fiche verbatim avec en-tête de provenance
6. `05-discourse.sh` — variante pour les forums Discourse
7. `06-imgur-album.sh` — lister et récupérer une galerie en pleine résolution
8. `07-planche-contact.sh` — trier un lot d'images d'un coup d'œil
9. `08-recadrer.sh` — lire une sérigraphie, un manuscrit, une ligne de tableau
10. `09-comparer.sh` — trancher une contradiction entre deux photos
11. `10-pdf-localiser.sh` — trouver un terme dans un manuel, détecter les scans
12. `11-pdf-detail.sh` — rendre et recadrer une page de schéma
13. `archive_imgs.py` — archivage définitif avec manifeste

## Compteur d'usage

| Script | Fois |
|---|---|
| `strip.py` | ~10 |
| `02-wayback.sh` | ~15 |
| `01-sonder.sh` / `03-telecharger.sh` | en continu |
| `08-recadrer.sh` | ~8 |
| `07-planche-contact.sh` | 4 |
| `10-pdf-localiser.sh` | 4 |
| `11-pdf-detail.sh` | 6 |
| `archive_imgs.py` | 2 |
| `06-imgur-album.sh` | 2 |
| `04-transcrire-forum.sh` | 2 (dont une avec repli de motif) |
| `05-discourse.sh` | 1 |
| `09-comparer.sh` | 1 |

## Ce qui manque, et qu'il faudra ajouter à l'intégration

- Aucun n'a de gestion d'erreur. `04-transcrire-forum.sh` a écrit un fichier
  vide sans rien dire quand son motif ne correspondait pas.
- Aucun ne vérifie le type MIME de ce qu'il reçoit ; c'était fait à la main.
- Les chemins sont absolus parce qu'ils devaient l'être (le répertoire courant
  est réinitialisé entre appels), mais ils sont en dur.
- `archive_imgs.py` porte son tableau `PLAN` de 29 entrées écrit à la main :
  c'est le travail éditorial, pas de l'outillage. Seule la mécanique
  recompression + manifeste est à reprendre.

Ce qui est là
Deux fichiers qui existaient déjà comme tels et que j'appelais en boucle :

strip.py — 12 lignes, HTML → texte, ~10 appels. C'est le plus rentable de tout le lot.
archive_imgs.py — recompression plafonnée + manifeste avec SHA-256 des originaux. Il porte son dict PLAN de 29 entrées écrit à la main : ça c'est du travail éditorial, pas de l'outillage. Seule la mécanique du bas est à reprendre.
Onze .sh qui restituent les blocs que j'exécutais en .venv/bin/python - <<PY … PY, avec leur enveloppe shell — c'est elle qui portait les chemins et les boucles, donc la retirer aurait fait perdre le plus utile. Numérotés dans l'ordre réel d'utilisation : sonder → wayback → télécharger → transcrire → images → PDF.

Les pièges sont dans les scripts, pas en commentaire de synthèse
J'ai laissé chaque piège à l'endroit exact où il m'est tombé dessus :

04-transcrire-forum.sh porte son repli de motif avec la mention que la première version, sans lui, a écrit « 0 messages transcrits » et produit un fichier vide sans rien signaler.
03-telecharger.sh ouvre sur les deux règles silencieuses : chemins absolus (un cd + tâche de fond m'a coûté un lot de cinq fichiers) et contrôle des tailles en lot (trois fichiers de 4 684 octets identiques = trois pages d'erreur).
10-pdf-localiser.sh et 11-pdf-detail.sh gardent la ligne de tableau réellement obtenue à l'extraction — CV utoff Voltage GS(off) VDS=–10V, I D=0 –1mA –5 1. –V 2. — pour montrer pourquoi il faut rendre l'image au lieu d'extraire le texte.
06-imgur-album.sh garde le piège du suffixe h : 40 Ko illisibles contre 3 Mo exploitables.
Le README donne l'ordre d'exécution, le compteur d'usage de chacun, et la liste de ce qui manque pour l'intégration — aucun n'a de gestion d'erreur, aucun ne vérifie le MIME de ce qu'il reçoit, je le faisais à la main.