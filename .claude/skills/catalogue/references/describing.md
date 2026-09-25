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

- **A PDF**: the title page, the table of contents, the first headings, the
  title block of a schematic (its name, its revision, its date), the maker's
  name and the model on the cover.
- **An image**: every text it shows — a label, a silkscreen, a model number, a
  screen, a handwritten note — and what is photographed: the part, the board,
  the tool, the defect.
- **A text or a conversation**: its title and its first lines; for a
  conversation pasted from another agent, the question it answers.
- **A directory**: what its files have in common, and the one that stands out.

## The name

- **In French, and it says what the thing is**: *Manuel de la station de
  soudage TC22*, *Photos des soudures froides de la carte d'alimentation*,
  *Schéma de l'amplificateur, révision B*.
- **Two to eight words.** No extension, no *fichier*, no *document*, no *PDF*.
  No date, unless the date is what tells it from its neighbours.
- **The library's words.** `.venv/bin/catalogue find` the object before naming it, and reuse what
  the library already calls it: *TC22* everywhere, not *TC-22* here and
  *tc 22* there.
- **An entry is named after its subject**, from what its items turned out to
  be: *Station de soudage TC22*, not *tc-22*.
- **A topic is named after its field**: *Outils de l'atelier*.

## The description

- **In French, one to three sentences.**
- **The words someone would search for**: the object and its model, the part
  numbers, the maker when the file shows it, the technique, the symptom, the
  kind of material — manuel, schéma, fiche technique, photo, facture,
  conversation, notes.
- **Where to look inside, when the file is long**: *p. 4-6 : réglage de la
  température ; p. 12 : codes d'erreur.*
- **For a directory**: what its files show together, and which one shows what
  when they are few.
- **What is read, never what is guessed.** A value, a model, a name is copied
  exactly as the file writes it. A doubt is written as one — *probablement
  un condensateur de découplage* — and becomes a question for the user.
- **Not the format or the size**: the tool knows them.
- **A topic's description says what belongs in it**, not what it holds now:
  *L'équipement de l'atelier : outils, instruments de mesure, consommables et
  leurs documentations.*

## The id's prefix

The tool draws 8 characters and adds them; the prefix is yours, given once, at
the first naming, and it never changes.

- **One to three short words**, lowercase ASCII, joined by hyphens, accents
  dropped: `manuel-tc22`, `photos-pannes`, `schema-ampli`, `etain`.
- **What the thing is**, so that a citation reads well:
  `[le manuel](id:manuel-tc22-a8f2c3d9)`.

## Examples

| Looked at | Name | Description |
|---|---|---|
| `sources/manuel.pdf`, 24 pages; p.1 reads *TC22 Soldering Station — User Manual* | Manuel de la station de soudage TC22 | Le manuel du fabricant, en anglais : mise en service, réglage de la température (p. 6-8), entretien de la panne (p. 10), codes d'erreur (p. 14). |
| `sources/Sans titre.jpg`, a photo of a board, two capacitors with bulging tops | Condensateurs gonflés sur la carte d'alimentation | Photo de deux condensateurs chimiques au sommet bombé, près du pont redresseur de la carte d'alimentation. Valeurs illisibles sur la photo. |
| `sources/facture.pdf`, 1 page, an invoice listing replacement soldering tips | Facture des pannes de rechange | Facture d'un lot de pannes de rechange pour la station TC22 : références, quantités et prix. |

And what not to write:

| Not | Because |
|---|---|
| *Photo* | says nothing a search could use |
| *Fichier PDF de 3 Mo* | the tool knows the format and the size |
| *Manuel de la Hakko FX-888* for a manual whose cover names no maker | a guess, written as a fact |
| a paragraph retelling the manual | a description decides whether to open the file; it does not replace it |
