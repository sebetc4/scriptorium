# Naming and describing

The rules for the name, the description and the id's prefix of a topic, an
entry or an item. Read by the `catalogue` skill and by the
`catalogue-describer` agent: one set of rules, so that a search finds the same
words whoever wrote them.

A description has one job: to let a session decide, from a few lines of `find`
or `ls -l`, whether to open the file. It is not a summary of the file, and it
never replaces opening it.

## Look before you write

**Never from the file's name alone.** Look inside, the cheapest way first —
`.venv/bin/catalogue peek <path>` before anything else:

| Kind | First | Then, only if the first did not settle it |
|---|---|---|
| PDF | `peek` — the page count and the text layer of the first pages | `peek --pages` further on (the table of contents, a title block); an image of a page only when its text layer is empty |
| image | `peek` — its size, and the date and camera it records | read it, to see what it shows |
| text, Markdown | `peek` — its first lines | read the rest |
| directory | `peek` — its files | a few of them, never all: three images at most |

**Where to look inside:**

- **A PDF**: the title page, the table of contents, the first headings, a
  title block or a colophon (its name, its revision, its date), the author's
  or the maker's name on the cover.
- **An image**: every text it shows — a label, a sign, a caption, a screen, a
  handwritten note — and what is photographed: the object, the place, the
  scene, the detail that made someone take it.
- **A text or a conversation**: its title and its first lines; for a
  conversation pasted from another agent, the question it answers.
- **A directory**: what its files have in common, and the one that stands out.

## The name

- **In the library's language, and it says what the thing is.** The tool
  names the standard files in the language `library/.catalogue.yaml`
  declares; the examples here come from a library in French: *Notice du
  lave-linge K-450*, *Photos de la façade avant les travaux*, *Plan du
  rez-de-chaussée, version B*.
- **Two to eight words.** No extension, and no word for *file*, *document* or
  *PDF*. No date, unless the date is what tells it from its neighbours.
- **The library's words.** `.venv/bin/catalogue find` the object before naming it, and reuse what
  the library already calls it: *K-450* everywhere, not *K450* here and
  *k 450* there.
- **An entry is named after its subject**, from what its items turned out to
  be: *Rénovation de la cuisine*, not *cuisine-2026*.
- **A topic is named after its field**: *Maison et travaux*.

## The description

- **In the library's language, one to three sentences.**
- **The words someone would search for**: the object, the place or the people
  it concerns, a model or a reference, the author or the maker when the file
  shows it, the subject, the kind of material — notice, plan, lettre, photo,
  facture, conversation, notes.
- **Where to look inside, when the file is long**: *p. 4-6 : installation ;
  p. 12 : messages d'erreur.*
- **The pages a text search cannot see.** `peek` reports the pages of a PDF
  with no text layer; the description says which they are and what they
  hold — *p. 3-15 : images sans texte, photos et schéma* — since a search of
  the text finds nothing there.
- **For a directory**: what its files show together, and which one shows what
  when they are few.
- **What is read, never what is guessed.** A value, a model, a name is copied
  exactly as the file writes it. A doubt is written as one — *probablement
  la façade nord* — and becomes a question for the user.
- **Not the format or the size**: the tool knows them.
- **A topic's description says what belongs in it**, not what it holds now:
  *La maison : les travaux, les équipements, les contrats et leurs
  documents.*

## The id's prefix

The tool draws 8 characters and adds them; the prefix is yours, given once, at
the first naming, and it never changes.

- **One to three short words**, lowercase ASCII, joined by hyphens, accents
  dropped: `notice-k450`, `photos-facade`, `plan-rdc`, `devis`.
- **What the thing is**, so that a citation reads well:
  `[la notice](id:notice-k450-a8f2c3d9)`.

## Examples

Fictional, like every example of this repository: the rules are the same
whatever a library holds.

| Looked at | Name | Description |
|---|---|---|
| `sources/notice.pdf`, 24 pages; p.1 reads *K-450 Washing Machine — User Manual* | Notice du lave-linge K-450 | La notice du fabricant, en anglais : installation (p. 6-8), programmes (p. 10), messages d'erreur (p. 14). |
| `sources/Sans titre.jpg`, a photo of a rendered wall, a crack running down from a window's corner | Fissure sous la fenêtre de la façade | Photo d'une fissure qui part de l'angle bas d'une fenêtre, sur un mur enduit. Sa largeur ne se lit pas sur la photo. |
| `sources/facture.pdf`, 1 page, an invoice for two replacement filters | Facture des filtres de rechange | Facture de deux filtres de rechange pour le lave-linge K-450 : références, quantités et prix. |

And what not to write:

| Not | Because |
|---|---|
| *Photo* | says nothing a search could use |
| *Fichier PDF de 3 Mo* | the tool knows the format and the size |
| *Notice du lave-linge Bosch* for a manual whose cover names no maker | a guess, written as a fact |
| a paragraph retelling the manual | a description decides whether to open the file; it does not replace it |
