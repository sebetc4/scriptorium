# Phase 5: The `fetch` Skill

---

## Status

**Current Status:** 🟢 Done (100% — 11/11)
**Started:** 2026-09-13
**Completed:** 2026-09-13
**Blocked By:** —

---

## Before Starting This Phase

> Read the previous phase in full before touching anything here: its notes,
> its unchecked tasks, and its unmet acceptance criteria. Skip this section
> only for the roadmap's first phase, which has no predecessor.

**Read First:**
1. The previous phase's `## Notes` section — what it found, decided, and
   left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Give web capture its own skill, and harden it with what the Electribe 2
investigation learned the hard way. One URL in, one document of the library
out — and every silent failure mode that investigation hit turned into a loud
one.

---

## Overview

### Why This Phase Matters

`core/fetch.py` works on a cooperative web. The sourcing inventory documents the
uncooperative one: expired certificates, user-agent filtering, `.pdf` URLs
answering HTTP 200 with an HTML signup wall, batches of files with rigorously
identical sizes because all three are the same error page.

Every one of those failures is silent by default. A capture tool that trusts
the status code and the extension archives error pages believing it archives
datasheets, and says nothing. This phase moves the module into its skill and
spends the rest of its budget on making it fail out loud.

### What It Enables

`sourcing` in Phase 6 can build on a fetch it trusts, instead of restating the
probing and MIME rules in its own tools.

### Out of Scope

- Following links. One URL, one document — a multi-page investigation is
  `sourcing`.
- Translating the captured document. `fetch` records the detected language;
  `translate` acts on it.
- The Wayback machine, forum parsing, image galleries. Those are investigation
  tools, Phase 6.

---

## Tasks

### The skill's prose
- [x] Write `SKILL.md` in English: one URL, one document, and the four things this skill refuses to do
- [x] Draw the boundary with `sourcing` in the skill's own words, so a reader lands on the right one without comparing descriptions
- [x] Document the client-rendered detection — much markup, little text — and the `RENDER=1` path through a headless browser

### The code
- [x] Move `core/fetch.py` and its tests into the skill — *it had none: a suite was written, see Notes*
- [x] Probe before downloading: report status, size, content type and effective URL, so a silent redirect is visible
- [x] Verify the MIME type of what came back; never trust the extension or the 200
- [x] Send a browser user agent, and fall back on a relaxed TLS check for hosts whose certificate has expired
- [x] Fail loudly on an empty extraction rather than writing an empty document
- [x] Use absolute paths throughout — the working directory is reset between tool calls, and a background write lands elsewhere in silence — *already true of the code; now guarded by a test*

### Closing
- [x] Keep the received page gzipped as the provenance piece, and write down why: a web page changes or disappears
- [x] Verification: capture a real page end to end, review the produced document, `make test` green

---

## Technical Details

### Files to Modify

```
.claude/skills/fetch/SKILL.md   written in full
core/fetch.py                    370 lines, moved and hardened
tests/                          the fetch suite, moved and extended
Makefile                        fetch
```

### Dependencies

Phase 2's layout, and the inventory in this roadmap's
`sources/sourcing/outillage-sourcing.md`
§1, which is the source of the hardening list.

### Constraints

- Playwright is not installed by default. The `RENDER=1` path must keep telling
  the user the two commands that install it, rather than failing obscurely.
- `sources/page.html.gz` is the only proof of what was captured. Nothing in the
  hardening may make it optional.
- `TO=` stays optional on `fetch` and mandatory on `import`: a web page declares
  its language, a PDF does not.

---

## Acceptance Criteria

- [x] A skill named `fetch` holds web capture, its script and its tests
- [x] Its `description` triggers on capturing a page into a document, and not on a multi-source investigation
- [x] A `.pdf` URL that answers HTML is reported as such and does not produce a document
- [x] A host with an expired certificate or a filtered user agent is captured rather than abandoned
- [x] An empty extraction raises instead of writing an empty `index.md` — *it refuses and returns 1, and the test for an extraction made of images alone is new*
- [x] The received page is still kept gzipped, with its provenance in `sources/meta.json`
- [x] `make fetch` works unchanged from the repository root
- [x] A real capture has been run and its document reviewed

---

## Notes

### The three silent failures this phase closes

From `sources/sourcing/outillage-sourcing.md`, each encountered at least once
and each costing time before it was noticed:

- **A `.pdf` in HTTP 200 that is HTML.** Signup wall, error page, redirect
  page. `file -b --mime-type` settles it in one call.
- **Three files of rigorously identical size.** Three error pages. Checking
  sizes across a batch catches what checking each file alone does not.
- **A `cd` followed by a background task.** The working directory is reset
  between tool calls; the files land somewhere else and nothing says so. It
  cost a whole batch. Absolute paths, everywhere.

### What probing buys

One line per URL, no bytes stored:

```
http=%{http_code} size=%{size_download} type=%{content_type} eff=%{url_effective}
```

On the investigation this established in three seconds that an entire forum was
answering 500 — and redirected the work to the archives instead of a dozen
failed downloads. `%{url_effective}` is what reveals a silent redirect.

### What was built, and where

- **`core/net.py`, new.** `get()` returns a `Response`: status, the
  `Content-Type` the server claimed, the effective URL, the body, and whether
  TLS was verified. `Response.line()` is the investigation's
  `curl -w "http=… size=… type=… eff=…"` probe, with `tls=unverified` appended
  when the fallback was used. `sniff()` reads the MIME type from the bytes. It
  lives in the core, not in the skill, per `docs/architecture.md` §2: Phase 6's
  tools are its second caller. Phase 6 should build on it rather than restate
  it.
- **`fetch.py`** moved into the skill and now retrieves through `net`, for the
  page and for every image. It refuses before writing anything when it gets an
  HTTP error, a PDF, a `.pdf` URL answering HTML, any non-page, or an
  extraction with no text. It also prints the probe line, reports a redirect
  and an unverified certificate, and records all four facts in
  `sources/meta.json`.
- **`tests/test_layout.py` split.** Its three repository-layout tests stayed at
  the root. Only the `fetch.LIBRARY` assertion moved, to
  `fetch/tests/test_fetch_layout.py`.

### Tested against a real server, not mocks

`fetch.py` had no tests (`docs/architecture.md` §7), so this phase wrote them
rather than moving them. The root `conftest.py` gained two fixtures, `web` and
`tls_web`: a local `http.server` whose answers each test writes, and the same
server over HTTPS with a self-signed certificate that `openssl` generates at
test time. Self-signed rather than expired, because both fail verification the
same way (`ssl.SSLCertVerificationError`) and an expired certificate cannot be
made portably without a new dependency. The fixtures are at the root because
Phase 6's suite will need them too.

The count went 126 → 158: 20 in `tests/test_net.py` and 12 in
`fetch/tests/test_capture.py`, with the layout test moved rather than added.

**Red first, and checked.** Every new test was watched failing on the missing
behaviour before the code was written, with one exception, stated below. Two
were also checked by mutation, because they had first failed on a stub rather
than on the specific defect: removing the TLS fallback turns the certificate
test red, and removing `Chrome/` from the user agent turns the filtering test
red. The first attempt at that second mutation reported green, but only because
`sed` had not matched: the user-agent string spans two lines. It was re-run on
a mutated copy.

**The exception:** the working-directory test passed from its first run, since
`LIBRARY` was already absolute. It is kept as a regression guard for the task,
not presented as proof of a fix.

### Two defects the tests found beyond the task list

- **`page.html.gz` was not the page as received.** It held the decoded text
  re-encoded as UTF-8, which changes the bytes of any page served in another
  encoding, and the digest in `meta.json` along with it. It now holds
  `response.body`. Through `--render` it holds the DOM the browser assembled,
  which is the only thing there is.
- **`sniff` missed HTML behind a byte-order mark or a leading comment.** Both
  are common on generated pages. The capture would have accepted those pages
  anyway, through the `Content-Type` fallback, but the sniff itself was wrong.

### The live verification

Run through `make fetch` against the real web, into a throwaway
`library/tmp-phase5/` that was deleted afterwards:

| URL | Result |
|---|---|
| `en.wikipedia.org/wiki/Light-emitting_diode` | captured: 817 kB → 89 kB of Markdown, 30 images, wide extraction; built to 40 pages and reviewed |
| `expired.badssl.com` | captured, `tls=unverified`, warning printed, `"tls_verified": false` |
| `arxiv.org/pdf/1706.03762` | refused, pointed to `make import` |
| a Wikipedia page that does not exist | refused, `http=404` |
| a w3.org sample PDF | refused, `http=403` — even with a browser's user agent |

The reviewed PDF shows what the procedure's pruning step exists for — `[edit]`
links, the infobox rendered as a broken table, " - Wikipedia" in the title — and
nothing the capture lost. It also shows **French quotation marks («») in an
English document**: the `lang:`-blind `smarty` that Phase 1's notes recorded,
met again on real content.

### Left out, on purpose

- **The batch-size check** ("three files of identical size"). Its root cause,
  error pages taken for files, is now caught by sniffing each response. What
  remains is a check across a batch of downloads, and `fetch` downloads one
  page. It belongs to `sourcing`'s batch downloader, Phase 6.
- **The mirror chain** listed for `core/net.py` in `docs/architecture.md`. No
  caller exists yet; the document now says Phase 6 adds it with the first one.
- **The `tld` deprecation warning** in the suite comes from a trafilatura
  dependency, not from this repository.
