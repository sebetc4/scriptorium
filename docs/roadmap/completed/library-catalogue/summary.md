# Summary — The Library Catalogue

---

## Where We Started

A discussion about the user's notebook reached beyond its own directory: to the
station's manual, the pages of its tips, the board holder, a draft, a kit's
document. It found them by listing the file system and wrote them down by hand,
by path, in the journal's **Material** section. That section was the problem
in three parts. Nothing said what a directory held without opening it: the
library had 23 directories of material under 9 topics, 14 of them invisible to
every tool. Many file names came from a camera or a paste. And a path broke at
the next rename — three renames in a few weeks, one of which turned `make test`
red.

The roadmap set out to make every directory describe itself in a manifest, to
cite by a permanent id, and to answer a question about the library in a few
lines, however large it grew; then to make the skills use that map.

---

## Where We Landed

Every directory of the user's library describes itself in a `manifest.yaml`:
its topics and entries are named and described, and so is every file they
hold. `make check-library` checks the map with the rest of the library, and is
clean. An agent reads the map through one entry point, `.venv/bin/catalogue` —
`find`, `ls`, `links`, `path`, `peek`, each answer twenty lines at most — and
keeps it through `sync` and `describe`, with five more commands that act only
on the user's word: `unused`, `remove`, `merge`, `rename`, `move`. The
`catalogue` skill holds the judgement the tool cannot, and its describing agent
takes the images and long PDFs out of the main conversation. The commands that
create an entry leave it on the map.

The skills use the map. A discussion answers from the agent's own knowledge by
default, searches only for the user's own case or a claim's source, and keeps a
guard against searching again; it cites by id and resumes from three short
answers instead of any source. An investigation keeps what it found in
`study/` and cites it by id. `pdf` and `fetch` look through the map before
writing. The notebook's journal, migrated to ids, followed two reorganisations
of the library without a single edit.

And the repository no longer holds anything of one library: its rules, its
examples, its tests and the core's standard names were rewritten so that any
user, with any kind of file, in any language, reads the same repository.

---

## What Each Phase Delivered

**Phase 0 — The Manifest.** The format, and `core/catalogue.py` to keep it:
`sync`, `describe`, the ids, the digests, the `id:` citations. `make
check-library` gained the catalogue's defects and its to-do counts, and the
guard refused a manifest edited by hand. The design settled at the opening held
without a change; the phase added the detail it left open — a directory
outside the roles, an empty directory, what a digest is compared against, how
far a move is followed.

**Phase 1 — Navigating the Library.** `find`, `ls`, `links` and `path`, one
entry point and their `make` targets. Measured on 500 more entries, every
answer kept its length, and the measurement found two costs no output length
would have shown — a slow YAML loader, and an `ls` computing lines it did not
print — both fixed within the phase.

**Phase 2 — The Catalogue Skill.** The skill, its rules for naming in a file
its agent shares, the commands that clean up and rename, `peek`, and the
describing agent, tried twice. It found that an id cannot simply be erased,
since the sessions citing it are never rewritten — hence retired ids — and it
closed a hole that let a path with `..` leave the library, at the moment the
commands became able to delete.

**Phase 3 — The Library Mapped.** The user's library synced, named and
described, and `make new`, `import` and `fetch` left mapping their entry. The
user's one review of the tree turned into two conventions of theirs and 34
renames; most of the describing needed no image, since the documents' study
already said what their sources were.

**Phase 4 — The Skills Use the Map.** The search rule and its guard,
citations by id, the resume from `sync`, `ls` and `links`, the notebook's
journal migrated. Two corrections from the user reshaped it: an
investigation's findings are not the user's sources, which gave the catalogue
`move`; and nothing may be written around one library, which rewrote 36 files
and gave a library its own language. The proof session found the user's kits
through the map, and answered from its own knowledge where the map added
nothing.

---

## What We Learned

- **A short description decides what gets opened.** A map read in bounded
  answers ties the cost of a question to the question, not to the library.
  The discussion that cost 102,719 fresh tokens before the map cost 52,119
  after it, on another subject; the comparison is loose, the direction is not.
- **What an append-only record points at needs a tombstone.** A session is
  never rewritten, so an id it cites can never vanish: removed or merged, it is
  retired, and still answers where it went.
- **Measure at scale, not only by eye.** Lengths looked right on the fixture;
  only 500 generated entries showed the time going to a loader and to lines
  never printed.
- **An agent call's cost is mostly fixed.** Rules and a resent context dominate,
  so the describing agent takes several entries per call — half the cost per
  entry — and a resumed agent is cheaper than a fresh one.
- **A rule is told apart by where its answer comes from, never by what one
  library holds.** A search rule first written with the user's equipment and
  projects would have misled every other user; examples are fictional.
- **A trigger needs a guard.** A rule that says when to search, without a
  limit and a record of what was searched, invites a search at every question
  to find out whether the library knows.
- **A convention read off one case can encode an accident.** Keeping an
  investigation's pieces in `sources/` came from a layout that predated the
  anatomy; the user's own account of what the files were overturned it.
- **A search that filters out what it looks for proves nothing.** A claim that
  a name occurred nowhere rested on a filter that excluded the very paths
  holding it; say what a search did not check.

---

## What We Are Leaving Open

- **The time of an answer grows with the library**, though its length does
  not: every command reads every manifest, about 70 ms for 500 entries. An
  index returns only if a search grows slow, rebuilt from the manifests.
- **No command prints the named tree**; the one review of it used a one-off
  script.
- **A rename inside a directory item splits it**, and the directory's item may
  end covering nothing of its own — harmless, and kept.
- **Standard names exist in English and in French**; a library in another
  language gets English ones until its own are added.
- **The describing agent reads three images per directory**; a directory whose
  every image matters takes a second call.
- **Outside this repository**: the user's global SessionStart hook injects a
  roadmap's phase and work log into every session, discussions included; and
  `session-review`'s `metrics.py` starts a slice where the previous task
  ended, charging a review's own cost to the next task — the session-review
  roadmap's to take up.
- **The discussion-and-illustration roadmap's transistor pilot is
  unblocked**; its opening clears the block it records.
