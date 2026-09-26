---
name: catalogue
description: Keep the library's map — the `manifest.yaml` in every directory of `library/`, which names and describes each topic, entry and file, and the ids they are cited by. Use to name or describe what the library holds, to sync the manifests after files were added, moved or renamed, when `make check-library` reports a manifest, an id or a citation, to clean up the sources nothing cites, or to rename a file whose name says nothing — cleaning up and renaming only on the user's word. Not for searching the library, which any skill does with `.venv/bin/catalogue find`; not for writing a document (the `pdf` skill), talking a subject through (`discussion`) or establishing a fact (`sourcing`).
---

# Keeping the library's map

Every directory of `library/` describes itself in a `manifest.yaml`: what a
topic is for, what an entry holds, what each of its files is. A session finds
its material through that map — a few lines of `find` or `ls` — instead of
listing the file system and opening what it finds. The map is only as good as
its words: a search finds what was described with the words it searches for,
and misses the rest.

**The tool does everything mechanical; this skill is the judgement.** `sync`
keeps paths, kinds, file counts and digests true to the disk. What no tool can
do is say what a file is, in the words someone will search for, and know when
to ask the user rather than guess.

**Reading the map is not this skill.** `find`, `ls`, `links` and `path` are
commands any skill runs, each carrying the one rule that concerns it. This
skill keeps the map true.

## When it applies

- **Naming and describing**: a new entry, sources added to one, an entry being
  studied, the items `ls` marks `to describe`.
- **After the disk changed**: the user added, moved, renamed or deleted files —
  `sync`, then what it reports.
- **A check reports the map**: `make check-library` prints a `manifest`, `id`
  or `citation` defect.
- **The user asks to clean up an entry, or to rename a file** whose name says
  nothing.

## The commands

Every command goes through one entry point, `.venv/bin/catalogue <command>`,
and prints at most 20 lines (`--limit N` for more). A target is a path under
`library/` or an id.

| Command | Does | Writes |
|---|---|---|
| `sync [<topic or entry>…]` | creates the missing manifests, adds an item for each file no item covers, follows a moved source by its digest, reports a named source vanished or changed | manifests |
| `describe <target> --name … --description …` | names and describes a topic, an entry or an item; the first naming draws its id | a manifest |
| `ls [<target>] [-l \| -ll]` | a topic's entries, an entry's items, with the markers `to describe`, `new`, `to review`, `gone` | nothing |
| `find <words> [--in <target>] [--text]` | what the library holds about the words | nothing |
| `links <target>` | what an entry or an item cites, and what cites it | nothing |
| `path <id>` | where an id is — or where it went | nothing |
| `peek <target> [--pages 2-5]` | a first look: a PDF's text layer, an image's size and date, a text's first lines | nothing |
| `unused <entry>` | the sources nothing cites and no tool derives from, each with its reason | nothing |
| `remove <item>… [--used]` | deletes the files of the items named and their lines, retiring their ids | files, a manifest |
| `merge <item>…` | folds items back into the named item above them, files untouched | a manifest |
| `rename <item> <new-name>` | renames one source file and its item, keeping the original name | a file, a manifest |
| `move <item> <new-path>` | moves one item's file or directory within its entry, across roles too, keeping its id, name and description | files, a manifest |

## What this skill refuses

- **Changing a source's content.** A source is what the user gave; it is
  read, described, renamed by the tool on the user's word — never edited.
- **Writing an id by hand.** An id comes from `describe`, which draws it and
  checks it is unique across the library. A manifest is written through the
  commands only, and the guard refuses an edit by hand.
- **An id in `document/`.** Citations serve the agent, not the reader: the
  document names its sources in its own words.
- **Describing a file from its name.** A name like `Sans titre.jpg` says
  nothing, and one like `manuel.pdf` may lie. A description is written after
  looking inside.
- **Removing, renaming or moving without the user's word.** The commands act
  on what their command line names; this skill names only what the user
  confirmed.

## Naming and describing

**Read [`references/describing.md`](references/describing.md) before naming
or describing anything.** It holds the rules for the name and the
description, and where to look inside each kind of file. The
`catalogue-describer` agent reads the same file, so that a name given in the
main conversation and one given by the agent follow the same rules.

**Describe with the library's words.** Before naming an object, `find` it: if
the library already writes *K-450*, it is *K-450* here too, not *K450*. A
search depends on the words being the same everywhere.

**The order**: the items first, then the entry, then the topic. An entry is
named from what its items turned out to be, not from its directory's name.

**A topic's description says what belongs in it**, not what is in it: it
stays true when the next entry arrives, and it tells a session where a new
entry goes.

### The heavy work goes to the agent

An entry with more than three images, or a PDF of more than a few pages, to
describe goes to the `catalogue-describer` agent: its pages and images stay out
of the main conversation. `sync` the entry first, then give the agent the
entry. It describes through `describe` and returns a summary, its questions
for the user, and its rename proposals. Relay the questions and the proposals
to the user as they are; apply the answers with `describe`, and the renames
the user accepts with `rename`.

One or two items are described in the conversation, by the same rules.

## Splitting and merging items

**An item is the unit someone would cite.** By default an entry has one item
per direct child of each role and one per other file or directory at its root:
`sources/images/` is one item, however many photographs it holds.

- **Split** when one file inside a directory item deserves its own name: the
  user refers to it alone, a discussion will cite it alone, or it is of
  another nature than the rest — the manual among the photographs.
  `describe <entry>/<path of the file>` gives it its own item, and the
  directory's item goes on covering the rest.
- **Merge** when items say the same thing: photographs of one repair
  described one by one, or a split that no longer serves. `merge <item>…`
  folds each back into the named item above it — a directory described first
  if there is none — and retires its id into that item, so a citation of it
  still leads somewhere. Then re-read the description of the item above: it
  now covers what was merged.

## When to turn to the user

Ask rather than guess. A guess written into a description is found by the next
search and taken for a fact.

- **A new source whose nature is unclear**: what it is, why it is here, what
  it belongs to.
- **A vanished source** — `sync` reports it, `ls` marks it `gone`: was it
  deleted on purpose, or moved out of the library? Deleted, `remove` retires
  its id; moved within the library, `sync` over the whole library follows it.
- **Something hard to identify**: a part, a model, a place, a person, a date
  the file does not write. Describe what is certain, and ask for the rest.
- **A name to find**: a file whose name says nothing, and whose content does
  not settle what to call it.
- **A copied directory** — `make check-library` reports an id held twice: ask
  which copy keeps its ids.
- **A source changed since it was described** — `ls` marks it `to review`:
  read it again and rewrite the description; ask only when the change is a
  surprise, a file replaced by another.

## Cleaning up, on the user's word

Only when the user asks. `unused` lists; the user decides; `remove` does what
they decided, and nothing else.

1. `unused <entry>` lists the sources nothing cites and no tool derives from,
   each with its reason.
2. Show the list to the user as it is, reasons included. *Nothing cites it* is
   not *nothing needs it*: a document written before ids existed cites
   nothing, and the reason says when the entry has one.
3. The user confirms all of it, part of it, or none.
4. `remove` exactly the items confirmed, each named by its path or its id. It
   refuses an item still cited or derived from; `--used` overrides that only
   for an item the user named knowing it is in use.

A removed item's id is retired, never erased: a session that cited it keeps
leading somewhere, and `path` says it was removed.

## Renaming, on the user's word

The manifest's name is what makes a file identifiable: no file needs renaming
for the agent's sake. A rename is proposed only for a flagrantly generic name,
because it helps the user when they search outside the manifest.

- **Generic**: `Sans titre.jpg`, `IMG_1234.jpg`, `licensed-image_002_aEns.jpg`,
  `WhatsApp Image 2026-09-21 at 15.57.37.jpeg`, `20260924_123413.jpg`,
  `document(3).pdf`. A short name the user chose — `k450.pdf` — is theirs.
- **Proposed as a list**, old name → new name, each drawn from the file's
  description. The new name is lowercase English words joined by hyphens, like
  the rest of the repository's tree, the extension kept:
  `crack-under-front-window.jpg`. Only the file name is English: the
  manifest's name and description stay in the library's language.
- **Renamed one `rename` at a time**, only those the user accepts. The
  original name stays in the manifest. `rename` refuses a file a tool derives
  from: `make rederive` finds it by name.

## Moving, on the user's word

`sync` follows a source the user moved by its digest. `move` is for what it
cannot follow: an item that changes role. It serves the anatomy — an
investigation's pieces taken out of `sources/` into `study/`, notes the user
gave taken out of `document/` into `sources/` — never the agent's taste in
names. The id, the name and the description go with the file, and so do the
items inside a moved directory; a directory left empty is removed. Proposed,
then done on the user's word, like a rename. Then re-read the descriptions
of the directories the move took a file out of or put one into: `ls` marks
them `to review`.

## After the disk changed

`sync` the entry the user touched, or the whole library when files moved
between entries: a move is followed only within what one `sync` covers. It
reports each manifest created, each new item, each move followed, each named
source vanished, each source changed since described. Then `ls <entry>`
gives the markers, which are the to-do list: describe what is `to describe`,
re-read what is `to review`, ask about what is `gone`.
