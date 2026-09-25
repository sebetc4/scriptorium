---
name: discussion
description: Hold a discussion with the user that is meant to become a document of this library, keeping a journal any later session resumes from. Use when the user wants to talk a subject through before its document exists, to resume or continue such a discussion in a new session, or to build a document from passages pasted out of conversations with other agents (ChatGPT, Gemini, Claude). Not for an ordinary exchange about the repository, its code or its skills; establishing a fact from outside sources is the `sourcing` skill, and writing index.md is the `pdf` skill.
---

# Discussing a document into being

**It produces knowledge and an outline, not a document.** Some documents have
no source but a conversation: the user knows what they want, an agent knows a
subject, and the document is what the two work out. The conversation is lost
when the session ends. What it established — what the user said, what was
decided, what was only claimed — survives only if it was written down while
it happened.

The journal is that record. It is written for one reader: the next session,
which has nothing else.

## When it applies

- **A subject talked through before its document exists.** The user wants a
  guide, a course, a summary, and the content will come out of the exchange.
- **Resuming one.** "On reprend la discussion sur…", "where were we on…": the
  journal exists, and the session starts from it.
- **Passages pasted out of other conversations.** The user copied an agent's
  answers from ChatGPT, Gemini or another Claude into `sources/`. They are the
  starting material of a discussion, not a source to transcribe.

It does not apply to an exchange about the repository itself — planning a
roadmap, fixing a skill, reviewing code. Nothing there ends in a document of
the library.

## What this skill refuses

- **Writing `index.md`.** The document is written by `pdf`, from the outline
  and the claims the journal holds.
- **Establishing a fact.** An agent's account does not become established by
  being repeated, by a second agent agreeing, or by sounding right. It is
  established by `sourcing`, which cites what establishes it.
- **Inferring what the user said.** A pasted passage carries the answers
  without the questions. What the user wanted is asked, never read back from
  what an agent replied.
- **Keeping a transcript.** The journal is what the conversation settled, not
  what was said in it. A transcript is what a resume must not have to read.
- **Editing `sources/`.** The pasted passages stay as the user left them.

## The journal

One directory per document, `library/<topic…>/<slug>/study/discussion/`, in
three layers, each from its template in this skill's `assets/`. It may exist
before `document/` does — a discussion usually starts before `make new`.

```
study/discussion/
  index.md             the entry, and the only file a resume reads
  topics/<subject>.md  the current state of one subject
  sessions/<date>.md   what one session covered, decided and replaced — never rewritten
```

A single file cannot last. Kept small, it overwrites what was said before;
kept whole, it grows with the conversation instead of with the document. The
index stays the size of what a resume needs. A topic holds one subject's
substance and is read when the discussion returns to it. The archive keeps
what was superseded, and no resume reads it.

### `index.md` — from `assets/index.md`

| Section | Holds | How it changes |
|---|---|---|
| **Where it stands** | three to five lines: the state, and the next question | **rewritten**, never appended to |
| **What the user said** | what frames the whole document: their goal, their reader, their level, their constraints — in their terms, dated | appended |
| **Decisions** | what shapes the whole document — its form, its title, its place — each with its reason, dated, and what was considered and rejected, with why | appended; one overturned moves to the session's **Replaced** |
| **Topics** | the map: one line per topic, its link, and where it stands | a line added per topic; its state rewritten |
| **Open questions** | the open ones only, each naming its topic | an answered question leaves: its answer goes to the topic, and the session's **Answered** records it |
| **To establish** | checkboxes, each a claim handed to `sourcing`, naming its topic | leaves once found: the result goes under **Established** in the topic |
| **Outline** | the document's plan, once the user has agreed it | revised with the user |
| **Material** | every file received — in `sources/`, or notes the user left elsewhere — one line each: what it is, which topics it fed | a line added per file |
| **Sessions** | one line per session, linked to its file | appended |

### `topics/<subject>.md` — from `assets/topic.md`

A topic is a subject the document will give a part or an entry to: a piece of
equipment, a technique, a project, a question the user keeps coming back to.
It is created at the first point that belongs to it. Everything the user said
that is not about the whole document goes in a topic — their equipment
included, when the document describes it.

| Section | Holds | How it changes |
|---|---|---|
| **What the user said** | on this subject: what they found, what they vouch for, what they want from it — in their terms, dated | appended |
| **Decisions** | what was settled on this subject, each with its reason, dated — and what was considered and rejected, with why | appended; one overturned moves to the session's **Replaced** |
| **Key points** | the substance the discussion produced: the explanation that worked, the example chosen, the analogy rejected and why, what the user found hard | condensed, never a transcript; a superseded point moves to the session's **Replaced** |
| **Claims** | what the document may state, under its status: *an agent's account* or *established* | a claim moves from one to the other, never silently |
| **Replaced** | one line per point superseded here: the date, what replaced it, a link to the session that holds the old one | appended |

### `sessions/<date>.md` — from `assets/session.md`

One file per session, named by its date; a second session the same day is
`<date>-2.md`. Written during the session, and never rewritten once it ends.

| Section | Holds | How it changes |
|---|---|---|
| **Covered** | what the session worked on, linking each topic it touched; for a pasted passage, the file, the agent if it can be told, what it covers, and what it refers to but does not contain | appended during the session |
| **Decided** | each decision taken, one line, linking to where it now lives | appended during the session |
| **Answered** | each question closed, its answer in one line, linking to its topic | appended during the session |
| **Replaced** | the superseded text itself, moved here whole, each piece linking to the topic that replaced it | appended during the session |

### What keeps the files from drifting

- **One fact lives in one place.** Its current state is in its topic, or in
  the index when it frames the whole document. Nothing is copied from one file
  to another: a link replaces the copy. A fact written twice is a fact that
  will disagree with itself.
- **A superseded point is never deleted, and never kept beside what replaced
  it.** It moves whole to the current session's **Replaced**, linking to the
  topic, and the topic's **Replaced** gains one line linking back. The topic
  says what is true now; the session says what was thought before.
- **A topic's file name is permanent.** Sessions link to it and are never
  rewritten. A subject that splits keeps its file, and the new part gets a new
  one.
- **Every link resolves.** `make check-library` checks each link of `index.md`
  and of the topics, and reports a journal still in one file.

**Three statuses, never mixed.** *Said by the user* lives in its own sections:
the user is the only source for their goal, their reader and their bench. *An
agent's account* is what this agent or the agent of a pasted passage asserted
— useful, unverified, and marked with whose account it is. *Established* points
at what establishes it: a `sourcing` journal, a datasheet, a measurement the
user made.

**A claim goes in when the document is likely to state it** — a value, a date,
a mechanism, a recommendation. Not every sentence of the exchange: the journal
that records everything is a transcript again.

**Written during the session, not after.** A session ends without warning. A
decision, a fact only the user has, a claim the document will rest on: each
is written when it appears, in its topic, and the session file gains its line.
**Where it stands** is rewritten whenever the state has moved, so that it is
never older than the last thing that mattered.

**A digest, sized by the document rather than by the conversation.** A
discussion that builds a course runs to hundreds of thousands of tokens, and
a resume that has to read it again costs that much each time. The journal is
what makes the next session cheap. An hour of talk adds a few lines to a
topic's **Key points**, not a page. **Key points** keeps what the document
will be written from: the explanation reached, not the three attempts before
it. **Decisions** keeps the rejected option with its reason, because that line
is what stops the next session from reopening the question. Before a pause,
and at the end of a session, condense: rewrite **Where it stands** and the
map's lines, merge the points that say the same thing, and move whatever was
superseded to the session's **Replaced**.

**Its headings stay as the templates have them; its content is in the
language of the discussion.** A topic's file name is short, lowercase, ASCII,
words joined by hyphens.

## Resuming

A new session reads `index.md`, and only `index.md`: not a topic, not a
session, not the previous transcript, not `claude --resume`. That is what
keeps a resume cheap — a file of a few thousand tokens against a conversation
of several hundred thousand — and it is why the index must be enough to say
where the discussion stands.

Find it with `find library -path '*/study/discussion/index.md'`, or by the
subject the user names. Then open by stating where it stands, in the index's
terms, and the next open question. Never ask again what **What the user
said** already answers.

**Load a topic when the discussion returns to it**, through its link in the
map, and not before. Every topic is read at the handover to `pdf`, since the
document is written from them.

**Look in `sessions/` only for an earlier point** — the user refers to
something the current topics no longer say. Follow the topic's **Replaced**
line to its session, or search the directory with `grep -r`. If it is nowhere,
ask, and write the answer down before going on: the gap is the journal's
defect, and it is repaired where it was found.

List `sources/` and compare it with **Material**. A file the index does not
name is new material: say so, and ask about it rather than opening it unasked —
a resume that reads every source again has lost what the journal saved.

**A journal found as a single file**, `study/discussion.md`, predates this
layout. Say so, and propose moving it into the three layers; do it once the
user agrees. What frames the whole document goes to the index. Each subject
becomes a topic, with its key points, its claims, and what the user said about
it. The answered questions and the dated session lines go to `sessions/`,
under the dates they carry. Then remove the old file.

## Passages pasted from other conversations

The user copies them by hand: a shared Gemini or ChatGPT link renders only in
a browser running JavaScript, and what reaches the repository is text.

1. **Leave the passage intact** in `sources/`. It is what was received.
2. **Record it** in **Material**, and in the session's **Covered**: the file,
   which agent if it can be told, what it covers.
3. **Take out the claims the document may rest on** into the topics they
   belong to, as an agent's account, citing the file. Drop the offers and the
   courtesy — *"Je te propose…"*, *"Voulez-vous que…"*. A plan the agent
   proposed is a candidate for the outline, marked as the agent's proposal:
   the user has not agreed to it.
4. **Two passages that agree do not establish a claim** — often they are two
   agents' answers to the same question, and agreement between them proves
   little. Two that disagree make an open question, or a claim to establish.
5. **What the passage refers to and does not contain** — a canvas, an image
   "ci-dessous", an earlier answer — is noted as missing, not guessed at.
6. **Ask what the user wanted** when they had those conversations: their goal
   and their reader are not in the passage.

## What the user brings

- **Notes the user wrote** are what the user said. Their points go under
  **What the user said** — in the index when they frame the document, in a
  topic otherwise — in their words, citing the file. A question in them goes
  under **Open questions**.
- **A photo, a measurement, a part they own** is received material, and
  belongs in `sources/`. What the agent reads in a photo — a joint that looks
  cold, a bridge between two pads — is an agent's account until the user
  confirms it or it is measured.
- **A file the user left outside the document's layout** — notes beside the
  `sources/` directory, or one level up in the topic — is theirs. Read it,
  never move it: `library/` is user content. Say where it would belong, and
  let them move it.

## Handing over

- **To `sourcing`**, when a claim the document will state as fact is a number,
  a date, a named part or a point two accounts disagree on. It goes under
  **To establish**; the investigation's result comes back to the topic's
  **Claims** as established, pointing at its `NOTES.md`.
- **To `pdf`**, once the user has agreed the outline. The document is written
  from the outline and the topics — their key points and their claims — never
  from a transcript. A claim still unverified is either established first or
  written as what it is — an order of magnitude, a typical value, an
  attribution — never as a fact the document vouches for.

The journal outlives the handover: when the document is revised, the
discussion resumes from it.
