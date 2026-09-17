# Outillage de sourcing — ce qui a servi, et sous quelle forme le rendre générique

> **Archive, remplacée le 2026-09-13.** Tout ce que ce document enseigne a été
> repris par la skill `sourcing` (`.claude/skills/sourcing/`) : la méthode dans
> `SKILL.md`, la carte des accès, datée et tenue à jour, dans
> `references/access-map.md`, les outils dans `scripts/`, avec leurs tests. La
> correspondance section par section est dans les notes de la phase 6 du
> roadmap `repo-overhaul`. Ce fichier est conservé tel quel, comme trace de
> l'enquête d'origine ; il n'est plus mis à jour.

Inventaire tiré d'une enquête réelle : reconstituer le circuit de mise sous
tension d'une Korg Electribe 2 à partir de quelques liens, dont **tous ceux du
forum principal étaient hors service**. Résultat : 46 images, 11 fils
transcrits, 8 PDF constructeur, 46 Mo.

Rien ici n'est théorique : chaque entrée a été employée au moins une fois, la
plupart entre trois et dix fois. Les invocations données sont celles qui ont
effectivement fonctionné.

Classement par valeur décroissante à l'intérieur de chaque section.

---

## 1. Récupération web

### 1.1 `curl` en repli de WebFetch — **indispensable**

WebFetch abandonne sur trois cas très fréquents, tous rencontrés :

| Cas | Symptôme | Repli |
|---|---|---|
| Certificat TLS expiré | `certificate has expired` | `curl -k` |
| Site qui filtre l'agent | `403 Forbidden` | `curl -A "<UA navigateur>"` |
| Domaine bloqué côté outil | `unable to fetch from <host>` | `curl` (a marché pour rien ici, mais coûte une seconde) |

```bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
curl -sk -A "$UA" -H "Accept-Language: en-US,en;q=0.9" -o sortie.html URL
```

Le certificat expiré de `korgforums.com` a bloqué WebFetch d'entrée. Sans ce
repli, l'enquête s'arrêtait au premier lien.

### 1.2 Sonder avant de télécharger — **le réflexe le plus rentable**

```bash
curl -sk -A "$UA" -o /dev/null \
  -w "http=%{http_code} size=%{size_download} type=%{content_type} eff=%{url_effective}\n" URL
```

Une ligne par URL, aucun octet stocké. C'est ce qui a permis d'établir en trois
secondes que le forum entier renvoyait 500 — et donc de basculer tout de suite
sur les archives au lieu de s'acharner. `%{url_effective}` révèle les
redirections silencieuses (la page pièces Syntaur redirigeait vers un index de
marques).

### 1.3 Vérifier le type MIME avant de traiter — **piège récurrent**

Plusieurs URL en `.pdf` ont répondu **HTTP 200 avec du HTML** : page d'erreur,
mur d'inscription, page de redirection. Un script qui fait confiance au code
de retour et à l'extension archive des pages d'erreur en croyant archiver des
fiches techniques.

```bash
m=$(file -b --mime-type fichier.pdf)
[ "$m" = "application/pdf" ] || echo "ce n'est pas un PDF : $m"
```

### 1.4 Chaîne de replis sur plusieurs miroirs

La fiche Sanyo du CPH6302 a demandé **quatre tentatives**. Modèle qui a servi
plusieurs fois : boucler sur une liste d'URL, s'arrêter au premier vrai PDF.

```bash
for u in URL1 URL2 URL3; do
  curl -sL --max-time 40 -A "$UA" -o tmp "$u"
  [ "$(file -b --mime-type tmp)" = "application/pdf" ] && { mv tmp cible.pdf; break; }
done
```

### 1.5 Téléchargements parallèles — avec **chemins absolus**

Le répertoire courant est réinitialisé entre deux appels d'outil : un `cd` suivi
de `&` en arrière-plan écrit les fichiers ailleurs, silencieusement. Ça m'a
coûté un lot entier.

```bash
S=/chemin/absolu/scratch
i=0; while read u; do
  i=$((i+1)); curl -sL --max-time 65 -A "$UA" -o "$S/out/$i.jpg" "$u" &
  [ $((i % 6)) -eq 0 ] && wait
done < urls.txt; wait
```

Par lots de 6 à 8. Au-delà, les serveurs commencent à jeter des connexions.

---

## 2. Wayback Machine — **le pilier de toute l'enquête**

Sans elle, zéro source primaire. À sortir en outil de premier rang, pas en
recours.

### 2.1 L'API CDX — la brique de base

```bash
curl -s "http://web.archive.org/cdx/search/cdx?url=<URL ou motif>\
&fl=timestamp,original,statuscode&filter=statuscode:200&collapse=urlkey&limit=N"
```

- suffixe `*` sur l'URL → correspondance par préfixe, sinon exacte
- `collapse=urlkey` → une ligne par URL distincte au lieu d'une par capture
- `filter=statuscode:200` → écarte les captures d'erreurs
- sortie : `timestamp original statuscode`, à recomposer en
  `https://web.archive.org/web/<timestamp>/<original>`

### 2.2 Tester la disponibilité en lot avant de télécharger

```bash
for t in 105619 117977 94641 122752; do
  r=$(curl -s "http://web.archive.org/cdx/search/cdx?url=site.com/viewtopic.php%3Ft%3D$t*&fl=timestamp,original&filter=statuscode:200&limit=5")
  echo "t=$t: ${r:-AUCUNE CAPTURE}"
done
```

Ça évite de lancer dix téléchargements pour en récupérer trois. Deux sujets sur
douze n'avaient aucune capture — su en cinq secondes.

### 2.3 **Résoudre un permalien de message vers son sujet** — la vraie difficulté

Découverte structurante : sur phpBB, **les permaliens de message (`p=NNNNNN`)
ne sont quasiment jamais archivés**, alors que les pages de sujet (`t=NNNNN`)
le sont presque toujours. Or les sources secondaires (articles, conversations,
citations) ne donnent que des `p=`.

Les huit `p=` de départ : zéro capture. Le site étant HS, impossible de résoudre
`p` → `t` en suivant la redirection.

Recette qui a débloqué la situation :

1. Lister les captures de l'index du sous-forum :
   `viewforum.php?f=<id>*` via CDX
2. Les télécharger toutes
3. Extraire les couples (identifiant de sujet, titre) :
   ```bash
   grep -ohE 'viewtopic\.php\?t=[0-9]+[^"]*" class="topictitle">[^<]*' *.html \
     | sed 's/" class="topictitle">/ | /' | sort -u
   ```
4. Chercher le titre voulu dans cette liste → on a le `t=`

C'est ce qui a livré `t=94641` (« Guts of a Virgin »). Les deux fils décisifs
ont fini par venir autrement — une source secondaire citait les `t=` —, mais
la recette reste la bonne parade générale.

**À généraliser :** un utilitaire « reconstruire l'index d'un forum archivé »
qui produit une table titre → identifiant, interrogeable. Applicable à phpBB,
vBulletin, Discourse, SMF.

### 2.4 `&view=print` sur phpBB — **gain considérable**

```
https://web.archive.org/web/<ts>/https://site/viewtopic.php?t=<id>&view=print
```

Tout le fil sur une page, sans navigation, sans signatures, sans avatars, sans
CSS. Un fil de 12 messages : 16 Ko en vue print contre 91 Ko en vue normale, et
un texte directement lisible. **Systématiquement préférer la vue print** quand
elle est archivée — et vérifier les deux au CDX.

Contrepartie : la vue print perd les liens d'images en pièce jointe. Sur un fil
riche en images, récupérer **les deux** variantes — texte depuis la print,
URL d'images depuis la normale. C'est ce qui a été fait pour « Guts of a
Virgin ».

### 2.5 Limites constatées

- L'endpoint `archive.org/wayback/available` sature vite (`429`). L'API CDX,
  elle, a encaissé une trentaine de requêtes sans broncher. **Préférer CDX.**
- La pagination d'un fil archivé est incomplète : seule la page 1 de « Guts of
  a Virgin » (4 pages) existait. Les `&start=15/30/45` renvoyaient une page
  d'erreur de 4 684 octets — **toujours contrôler la taille des réponses en
  lot** : trois fichiers de taille rigoureusement identique = trois erreurs.

---

## 3. HTML → texte

### 3.1 `strip.py` — **utilisé une dizaine de fois, à scripter en premier**

Le plus rentable de tout l'outillage, et le plus court.

```python
import re, html, sys
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
s = re.sub(r'(?is)<script.*?</script>', '', s)
s = re.sub(r'(?is)<style.*?</style>', '', s)
s = re.sub(r'(?is)<!--.*?-->', '', s)
s = re.sub(r'(?i)<br\s*/?>', '\n', s)
s = re.sub(r'(?i)</(p|div|tr|li|h[1-6]|td)>', '\n', s)
s = re.sub(r'<[^>]+>', '', s)
s = html.unescape(s)
s = re.sub(r'[ \t]+', ' ', s)
s = re.sub(r'\n\s*\n\s*\n+', '\n\n', s)
print(s.strip())
```

Points qui comptent, tous appris à la dure :

- `errors='replace'` — les vieux forums sont en latin-1 mal déclaré
- retirer `<script>`/`<style>` **avant** les balises, sinon leur contenu
  remonte dans le texte
- `<br>` et fermetures de blocs → saut de ligne **avant** de tout dépouiller,
  sinon les messages se collent en un pavé illisible
- `html.unescape` **après** le dépouillage

`trafilatura` est déjà dans `requirements.txt` et vise mieux sur un article de
presse. Sur une page de forum archivée par la Wayback (avec sa barre d'outils
injectée), ce dépouillage brutal a donné de meilleurs résultats — il ne tente
pas de deviner le contenu principal.

### 3.2 Discourse : `.json` plutôt que du grattage — **à tenter partout**

```bash
curl -sL -A "$UA" "https://forum.exemple.com/t/<slug>/<id>.json"
```

```python
d = json.load(open("fil.json"))
for p in d['post_stream']['posts']:
    texte = re.sub(r'<[^>]+>', '', p['cooked'])
    print(p['username'], p['created_at'][:10], texte)
```

Auteurs, dates, corps propre. Aucune regex fragile. A marché du premier coup
sur Syntaur alors que les pages HTML du même site renvoyaient 403.

**Signature à reconnaître :** `<meta name="generator" content="Discourse">`, ou
des URL en `/t/<slug>/<id>`. Vaut aussi le coup à l'aveugle : ça coûte une
requête.

### 3.3 Repli quand la première regex ne trouve rien

Les gabarits de forum varient. Chaîner les motifs, du plus précis au plus
large, **et signaler quel motif a servi** :

```python
posts = re.findall(r'(?is)<div[^>]*class="[^"]*\bmessage\b[^"]*"[^>]*>(.*?)</div>\s*</div>', s)
if not posts:
    posts = re.findall(r'(?is)itemprop="text"[^>]*>(.*?)</div>', s)
```

Un script qui écrit `0 messages transcrits` sans broncher produit un fichier
vide qu'on croit plein. C'est arrivé. **Faire échouer bruyamment sur zéro
résultat.**

### 3.4 Extraire les images **avec leur contexte**

Une URL d'image seule ne se légende pas. Capturer les ~400 caractères de texte
qui la précèdent donne la légende presque toute faite :

```python
for m in re.finditer(r'imgur\.com/([A-Za-z0-9]{7})h?\.jpg', s):
    ctx = re.sub(r'<[^>]+>', ' ', s[max(0, m.start()-400):m.start()])
    print(m.group(1), '<<', html.unescape(re.sub(r'\s+', ' ', ctx)).strip()[-160:])
```

C'est ainsi que chaque photo de démontage a pu être associée au circuit intégré
qu'elle illustre, sans ouvrir les 12 images une par une.

---

## 4. Images — **c'est là que se gagne le plus de temps**

### 4.1 Planche contact — **le meilleur rapport bénéfice/effort de tout l'outillage**

Trois usages, trois fois décisif : 15 photos de réparation, 15 photos de
démontage, 9 pages de schémas. À chaque fois : une planche, un regard, deux
images retenues.

```python
from PIL import Image, ImageDraw
import glob, os

fichiers = sorted(glob.glob("dossier/*.jpg"))
cols, cw, ch = 4, 560, 340
rows = (len(fichiers) + cols - 1) // cols
planche = Image.new("RGB", (cols*cw, rows*ch), "white")
d = ImageDraw.Draw(planche)
for i, f in enumerate(fichiers):
    im = Image.open(f); im.thumbnail((cw-8, ch-28))
    x, y = (i % cols)*cw, (i // cols)*ch
    planche.paste(im, (x+4, y+24))
    d.text((x+6, y+6), os.path.basename(f), fill="black")
planche.save("planche.png")
```

**Le nom de fichier écrit sur chaque vignette est non négociable** — sans lui,
on voit l'image intéressante sans savoir laquelle c'est.

Viser ~2000 px de large : au-delà c'est redimensionné à la lecture et les
vignettes deviennent illisibles.

Le dépôt a déjà `make preview` (planche contact d'un document construit). Même
idée, autre entrée : **un dossier d'images quelconque**. À factoriser.

### 4.2 Recadrage fractionnaire + agrandissement — **une demi-douzaine de fois**

Lire une sérigraphie de PCB, un schéma manuscrit, une ligne de nomenclature.
Coordonnées **en fractions**, jamais en pixels : ça permet de viser sans
connaître les dimensions.

```python
im = Image.open(src); w, h = im.size
im.crop((int(w*0.05), int(h*0.15), int(w*0.62), int(h*0.85))) \
  .resize((1500, hauteur_proportionnelle), Image.LANCZOS) \
  .save(dst)
```

`LANCZOS` à l'agrandissement : sur du texte sérigraphié de 0,5 mm, l'écart avec
le rééchantillonnage par défaut décide entre « lisible » et « pas lisible ».

C'est ce qui a permis de lire `DT2`, `DT37`, `C188`, `J4` sur les photos, et de
trancher trois désignations contradictoires dans les sources écrites.

### 4.3 Composite côte à côte — pour trancher une contradiction

Deux photos du même objet, prises par deux personnes, collées côte à côte au
même cadrage : c'est ce qui a réglé la question `DT2` / `DP2` / `D2`.

```python
out = Image.new("RGB", (2*L, H), "white")
out.paste(recadrage_a, (0, 0)); out.paste(recadrage_b, (L+20, 0))
```

**À généraliser :** `compare-crops <imgA> <imgB> --region x0,y0,x1,y1` en
fractions, avec les deux recadrages normalisés à la même taille.

### 4.4 Albums Imgur : passer par l'API

Une page d'album Imgur est montée en JavaScript : le HTML statique ne fait que
~7 Ko et ne cite qu'**une seule** image. L'API publique rend la liste complète :

```bash
curl -s "https://api.imgur.com/post/v1/albums/<ALBUM_ID>?client_id=546c25a59c58ad7&include=media"
```

```python
d = json.load(open("album.json"))
for m in d['media']:
    print(m['id'], m['ext'], m['width'], 'x', m['height'])
```

**7 Ko de HTML → 15 images en pleine résolution.** Sans ça, la galerie de
réparation entière était perdue.

Deux détails :

- le `client_id` est celui du client web public d'Imgur ; il peut cesser de
  fonctionner, prévoir un message clair plutôt qu'un plantage
- **suffixe de vignette** : `https://i.imgur.com/<id>h.jpg` est une miniature,
  `https://i.imgur.com/<id>.jpg` (ou `.jpeg`) l'original. Les pages de forum ne
  citent que les vignettes. **Retirer le `h` final** — c'est la différence
  entre 40 Ko inexploitables et 3 Mo lisibles.

### 4.5 Archivage avec manifeste — **provenance à la collecte, jamais après**

Pour chaque image : empreinte SHA-256 de l'**original** (avant recompression),
URL d'origine, légende, dimensions d'origine et stockées.

```python
{"fichier": "...", "origine": "<URL>", "legende": "...",
 "dimensions_origine": [w, h], "dimensions_stockees": [w, h],
 "sha256_original": "...", "octets": 123456}
```

Deux jours plus tard, on ne sait plus d'où vient une image. Le manifeste a servi
en permanence à rédiger les notes. L'empreinte permet de prouver qu'on n'a pas
altéré la pièce.

Recompression : côté long plafonné à 2600 px, qualité 88, progressif. **36 Mo
→ 21 Mo sans perte de lisibilité de sérigraphie.** Garder le plein format pour
les deux ou trois pièces décisives (ici 4200 px pour la zone d'alimentation).

---

## 5. PDF

### 5.1 Localiser un terme dans un manuel entier

```python
import pypdfium2 as p
d = p.PdfDocument(chemin)
pages = [i+1 for i in range(len(d)) if "CPH6302" in d[i].get_textpage().get_text_range()]
```

Quatre manuels, 79 pages, une seconde : le terme cherché était en page 22, 12,
12 et 23/26. Sans ça, il faut feuilleter.

### 5.2 **Détecter les pages scannées** — distinction essentielle

```python
t = d[i].get_textpage().get_text_range()
if len(t) == 0:
    ...  # page image : la rendre, ne pas espérer en extraire du texte
```

Les schémas des service manuals Korg rendaient **0 caractère** : purement
graphiques. Un script qui ne fait qu'extraire du texte conclut « rien dans ce
PDF » alors que l'essentiel y est. `len(texte) == 0` → basculer en rendu
d'image.

### 5.3 Planche contact des pages d'un PDF

Même principe qu'en 4.1, appliqué aux pages. 24 pages de service manual rendues
en une planche → la page « Power » repérée d'un coup d'œil à son cartouche.

```python
im = d[i].render(scale=2).to_pil()
```

`scale=2` suffit pour trier. Le dépôt a déjà ce rendu dans sa boucle de
relecture (`pypdfium2`, skill `pdf-doc` §3) — c'est la même brique, à exposer
pour n'importe quel PDF, pas seulement pour les documents construits.

### 5.4 Rendu haute résolution + recadrage, pour lire un schéma

```python
im = d[3].render(scale=6).to_pil()   # ~7100 × 5000 px sur un A3
w, h = im.size
im.crop((int(w*0.34), int(h*0.48), int(w*0.72), int(h*0.80))).save(dst)
```

`scale=6` rend les valeurs de composants et les repères lisibles sur un schéma
A3. C'est ce qui a permis de lire `F1 / CPH6302`, `IC20 / S-8520`, le brochage
S/G/D, et le contact de coupure du jack `DJ1`.

Procédure : `scale=2` pour trouver la page → `scale=6` + recadrage pour lire.

### 5.5 **Ne pas faire confiance à l'extraction de tableaux**

Le tableau de caractéristiques du CPH6302 est sorti avec les colonnes
entrelacées, illisible :

```
CV utoff Voltage GS(off) VDS=–10V, I D=0 –1mA –5 1. –V 2.
```

Rendu en image, la même ligne se lit sans effort : `V_GS(off)`, conditions,
min −1,0, max −2,5, unité V. **Sur un tableau de fiche technique, rendre et
lire l'image.** L'extraction textuelle ne sert qu'à *localiser* la page.

---

## 6. Ce qui est bloqué, et ce qui marche quand même

Carte relevée sur cette enquête. Évite de réessayer à l'aveugle et oriente vers
la bonne porte.

### Murs constatés

| Cible | Comportement |
|---|---|
| **Reddit** | 403 sur `www`, `old`, `api`, `.json`, `.rss`, et WebFetch. Aucune capture Wayback du fil. **Considéré comme inaccessible.** |
| **ModWiggler** | 403 sur WebFetch et curl avec UA navigateur |
| Agrégateurs de fiches techniques | alldatasheet, datasheetq, datasheetbank, datasheets360, chipfind : 403 systématique |
| manualzz, elektrotanya, scribd | mur d'inscription ou 403 |
| Mouser (lien direct vers PDF) | renvoie du HTML en 200 |
| DuckDuckGo HTML | 202 + page de défi |

### Portes qui s'ouvrent

| Besoin | Ce qui marche |
|---|---|
| Fiche technique de composant | **Site du fabricant en direct** : `assets.nexperia.com/documents/data-sheet/<REF>.pdf`, `sameskydevices.com/product/resource/<ref>.pdf`. Sinon, miroirs obscurs — `1688eric.com` a livré la fiche Sanyo que cinq agrégateurs refusaient. |
| Service manuals de synthétiseurs | **`polynominal.com`** et **`vintagesynthparts.com`** servent des PDF en direct, sans inscription. Ressource de premier ordre pour l'électronique musicale. |
| Documentation constructeur | Le site officiel, en direct. `cdn.korg.com` a servi un manuel de 112 pages sans difficulté. |
| Forum Discourse | l'endpoint `.json` (§3.2) |
| Contenu d'une page morte | Wayback (§2) |
| Contenu indexé d'une page morte | La recherche web restitue du contenu que le moteur a indexé, même quand la page renvoie 500. Complément utile — mais **c'est du second rendu, pas une pièce** : à ne jamais citer comme source primaire. |

### Le principe qui s'en dégage

**Quand une pièce est introuvable, chercher la même information ailleurs plutôt
que d'insister sur la porte fermée.** Le schéma d'alimentation de l'Electribe 2
n'existe pas publiquement. Ceux de trois autres machines Korg de la même
famille, si — et ils contiennent la pièce cherchée, son repère, son brochage.
C'est cette bifurcation qui a produit le meilleur résultat de l'enquête.

---

## 7. Méthode — ce qui n'est pas du code mais a autant compté

### 7.1 Un journal tenu en continu, à trois statuts

`NOTES.md` avec, dès le premier jour, trois catégories séparées :

- **ce qui est établi** — avec citation verbatim et source
- **ce qui est hypothèse** — de qui, sur quelle base, avec les réserves
- **ce qui reste à chercher** — en cases à cocher

Rédigé **pendant** la collecte, pas après. Trois fois, une source ultérieure a
fait basculer un point d'une catégorie à l'autre ; sans le journal, la nuance se
perd et le document final affirme ce qui n'était qu'une supposition.

Les cases cochées doivent dire **ce qu'on a trouvé**, y compris « dépouillé,
rien d'exploitable ». Deux fils ont été ouverts deux fois faute de l'avoir noté.

### 7.2 Séparer la pièce de sa transcription

Trois niveaux, jamais mélangés :

| Niveau | Rôle |
|---|---|
| `raw/*.html.gz` | ce qui a été reçu, intact — la preuve |
| `threads/*.md` | transcription verbatim, en-tête de provenance |
| `NOTES.md` | l'analyse, qui cite les deux précédents |

Un en-tête de provenance sur chaque transcription : URL d'origine, URL
d'archive, date de récupération, et **les conditions de la collecte** (« le
forum renvoyait 500, seule la Wayback était accessible »).

### 7.3 Remonter à la source primaire

Le forum affirmait « MOSFET CPH6302 ». La fiche Sanyo a confirmé canal P,
donné le brochage, le marquage boîtier `JB` — qui est le seul moyen pratique de
retrouver la pièce sur la carte — et permis de vérifier par le calcul que le
composant est correctement dimensionné.

Un forum donne une piste. Une fiche constructeur donne un fait. **Toujours
remonter d'un cran.**

### 7.4 Recouper les témoignages visuels

Trois photos de la même zone de carte, par trois personnes, sur deux modèles
différents, à trois années d'écart. Convergence → le plan est stable entre
modèles, donc le diagnostic est transposable. Et la sérigraphie tranche trois
désignations contradictoires des sources écrites.

**Une photo est une pièce à charge comme une autre**, et souvent plus fiable
qu'un souvenir de forum.

### 7.5 Suivre la piste que la source a abandonnée

L'auteur du fil principal signale en passant avoir vu « quelque chose de
similaire dans le service manual du microKORG », puis écarte l'idée. C'est
exactement là qu'était le meilleur filon : quatre manuels officiels, le code
pièce Korg, le repère, le brochage, et le mécanisme du jack dessiné par le
constructeur.

**Ce qu'une source mentionne sans exploiter mérite un détour.**

---

## 8. Ce qui mérite de devenir un script

Par ordre de rentabilité. Les quatre premiers valent à eux seuls l'extraction.

| Script | Fait quoi | Fréquence d'usage ici |
|---|---|---|
| `contact-sheet <dossier\|pdf>` | planche contact d'un dossier d'images **ou** des pages d'un PDF, vignettes nommées | 4 fois, décisif à chaque fois |
| `html2text <fichier>` | §3.1, avec repli sur l'extraction Discourse si le site le permet | ~10 fois |
| `crop <image> --region f,f,f,f [--scale N]` | recadrage en fractions + agrandissement LANCZOS ; `--compare <img2>` pour le composite | ~8 fois |
| `wayback <url> [--list\|--get\|--print-view]` | CDX, disponibilité en lot, récupération, préférence automatique pour `&view=print` | ~15 fois |
| `fetch-checked <url> -o <fichier>` | UA navigateur, `-k`, sonde, **vérification MIME**, chaîne de miroirs | en continu |
| `pdf-find <pdf> <terme>` | pages contenant le terme + **signalement des pages sans couche texte** | 4 fois |
| `pdf-render <pdf> <page> --scale N [--region f,f,f,f]` | rendu haute résolution + recadrage | 6 fois |
| `imgur-album <id>` | liste complète via API, résolution pleine taille, dé-vignettage | 2 fois, sans quoi 15 images perdues |
| `archive-images <dossier> --dest <d> --manifest` | recompression plafonnée + manifeste avec SHA-256 des originaux | 2 fois |
| `forum-index <domaine> <forum-id>` | reconstruit titre → identifiant de sujet depuis les listings archivés (§2.3) | 1 fois, débloquant |

### Deux invariants à tenir dans tous

1. **Chemins absolus.** Le répertoire courant est réinitialisé entre les appels ;
   un `cd` + tâche de fond écrit ailleurs, en silence.
2. **Échouer bruyamment sur un résultat vide.** « 0 message transcrit », trois
   fichiers de taille identique, un PDF qui est du HTML : tous rencontrés, tous
   silencieux par défaut, tous coûteux.

### Ce qui n'a pas besoin d'être un script

Les regex d'extraction propres à un gabarit de site, et les chaînes de miroirs
propres à un type de document. Ça change trop vite. En revanche, **la carte de
la §6 mérite d'être maintenue** : savoir d'emblée que Reddit est fermé et que
`polynominal.com` sert des PDF en direct vaut plusieurs dizaines de requêtes
perdues.


### Review final

Ce que j'ai retenu comme méritant l'extraction
Les quatre qui valent à eux seuls l'opération :

Planche contact — le meilleur rapport bénéfice/effort de tout l'outillage. 15 photos → une planche → un regard → deux images retenues. Employé 4 fois, décisif à chaque fois. Le dépôt a déjà cette brique dans make preview et dans la boucle de relecture PDF : c'est la même, à exposer pour un dossier d'images ou un PDF quelconque.
html2text — le strip.py de la §3.1, une dizaine d'usages. Vingt lignes, mais avec quatre détails qui décident entre « lisible » et « pavé illisible » (ordre des opérations, errors='replace', <br> avant dépouillage).
Recadrage fractionnaire + LANCZOS — coordonnées en fractions, jamais en pixels. C'est ce qui a permis de lire DT2, DT37, C188 sur les sérigraphies et de trancher trois désignations contradictoires.
Wayback/CDX — sans elle, zéro source primaire sur cette enquête.
Trois choses que je n'aurais pas su avant de les rencontrer
Les permaliens de message phpBB ne sont quasi jamais archivés, les pages de sujet presque toujours. Mes huit liens de départ étaient tous en p= : zéro capture. La parade — reconstruire l'index du forum depuis les listings archivés — est en §2.3.
&view=print sur phpBB : 16 Ko de texte propre contre 91 Ko de page complète, tout le fil sur une page.
Le suffixe h d'Imgur : les forums ne citent que les vignettes. Retirer le h final, c'est 40 Ko inexploitables contre 3 Mo lisibles.
Les pièges qui m'ont coûté du temps, tous silencieux
Trois échecs qui ne lèvent aucune erreur : un .pdf en HTTP 200 qui est du HTML, trois fichiers de taille rigoureusement identique qui sont trois pages d'erreur, et un cd suivi d'une tâche de fond qui écrit ailleurs parce que le répertoire courant est réinitialisé entre appels. D'où les deux invariants en fin de §8 : chemins absolus et échouer bruyamment sur un résultat vide.

J'ai aussi consigné en §6 la carte de ce qui est bloqué (Reddit fermé sur tous ses endpoints, agrégateurs de fiches techniques en 403 systématique) et de ce qui s'ouvre — polynominal.com et vintagesynthparts.com servent des service manuals en direct, sans inscription. Cette carte-là mérite d'être maintenue même si les regex de scraping, elles, ne valent pas d'être figées.