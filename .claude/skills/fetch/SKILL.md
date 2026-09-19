---
name: fetch
description: Capture one web page, known by its URL, as a document of this library. Use when given a URL to turn into a document here. One URL, one document — it does not follow links, does not reproduce the site's layout, and does not translate (that is the `translate` skill). Not for an investigation across several sources that are not known in advance — that is the `sourcing` skill.
---

# Web capture

**One URL, one document.** The tool retrieves a page, extracts its content
without the site's navigation, downloads its images, keeps the page exactly as
it was received, and writes an ordinary document of the library. `make build`
then gives it the repository's art direction, as for any other document. From
there on the document is written, built and reviewed with the `pdf` skill.

The script is this skill's `scripts/fetch.py`, reached through `make fetch` from
the repository root. The retrieval underneath it — the probe, the MIME check,
the browser user agent, the TLS fallback — is `core/net.py`, shared with
`sourcing`.

## `fetch` or `sourcing`?

Ask two questions. **How many sources, and were they known before starting?**

- **One URL, given up front, whose content *becomes* the document** → this skill.
  The output is a `document/index.md` under `library/`.
- **Several sources, found along the way and checked against each other** — live
  pages, archived pages, forums, PDFs, photographs — → `sourcing`. The output is
  a journal and its pieces, never a document.

A request that starts with a URL is not necessarily this skill. "Capture this
article" is. "Find out from this forum thread and whatever it links to how the
power circuit works" is `sourcing`, even though it also starts from one URL: the
answer is not on that page, it has to be established.

## What this skill refuses

- **Following a link.** One URL, one document. To gather several pages, run it
  several times and assemble them by hand. Collecting and cross-checking pages
  is `sourcing`.
- **Translating.** It records the page's language. Translation is `translate`.
- **Reproducing the site's layout.** On purpose: the document carries the
  repository's art direction, not the site's.
- **Capturing what is not a web page.** A PDF URL is refused with a pointer to
  `make import` (the `pdf` skill). An image or any other file is refused too.

## Capturing

```bash
make fetch URL=https://example.org/article DOC=watch/article [TO=fr] [RENDER=1]
```

`TO` is optional here, where `make import` requires it: a web page declares its
language, a PDF does not. Without `TO`, the document takes the page's language.
**Offer a translation**: the tool prints the detected language, and if it
differs from the user's, ask whether they want the document translated before
reviewing it. Then ask about the theme, as for every document (the `pdf` skill,
*What to ask*).

The first line printed is the probe:

```
  http=200 size=840124 type=text/html; charset=UTF-8 eff=https://…
```

Status, size, the content type the server claimed, and the **effective URL**,
which is where the request actually ended up. Read it: a page that redirects to
an index of brands still answers 200.

It writes — `docs/document.md` says what each directory of a document is for:

| Path | Content |
|---|---|
| `document/index.md` | front matter + extracted content, to prune |
| `document/assets/` | the downloaded images, recompressed |
| `study/extracted.md` | the raw extraction, an immutable reference |
| `sources/page.html.gz` | **the page as it was received**, byte for byte |
| `study/meta.json` | provenance: URL, effective URL, HTTP status, content type, TLS verification, date, SHA-256 digest, images that failed |

**`sources/page.html.gz` is the only proof of what was captured**, because a
web page changes or disappears and cannot be asked for again. It holds the
received bytes, not a re-encoding of them. Never delete it, and never make it
optional.

## What it refuses out loud

On an uncooperative web every failure is silent by default: a tool that trusts
the status code and the extension archives error pages while believing it
archives documents. Each case below was met in a real investigation. The tool
stops **before writing a single file** and prints why, with the probe line.

| What came back | What the tool does |
|---|---|
| An HTTP error — 403, 404, 500 | refuses: `the page answered HTTP 500` |
| A `.pdf` URL answering **HTML** — a signup wall, an error page | refuses: `a .pdf URL answered text/html` |
| A real PDF | refuses, and points to `make import` |
| An image, or any other non-page | refuses: `this URL serves image/png` |
| An extraction with **no text** — images only, markup only | refuses: `the extraction has no text` |

What came back is **read from the bytes**, never taken from the name or from the
`Content-Type` header, since both can lie.

And two cases it gets through, saying so rather than giving up:

- **A host that filters user agents** gets a browser's user agent from the first
  request.
- **An expired or unverifiable certificate** is retried over an unverified
  connection. The probe line ends in `tls=unverified`, a warning is printed, and
  `study/meta.json` records `"tls_verified": false`. Mention it to the user
  when the document's provenance matters.

A redirect is printed as `! redirected: <url> → <effective url>`, and recorded.

Images get the same treatment. An image link that answers an HTML page is listed
in `study/meta.json` under `image_failures` as `answered text/html, not an
image`, rather than as an obscure decoding error.

Everything is written under the repository's `library/`, resolved to an
absolute path: the working directory the tool is run from changes nothing.

## Client-rendered pages

A page built in React or a similar framework delivers almost nothing as static
HTML. The tool detects it — a lot of markup for very little text — and says so.
When the page yields no text at all, it refuses and suggests the same thing.
Run it again with `RENDER=1`, which goes through a headless browser.

Playwright is not installed by default, and the error message gives the two
commands:

```bash
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
```

The probe still runs first, so a PDF or an HTTP error is refused before a
browser is started. Through a browser, `sources/page.html.gz` holds the page the
browser assembled rather than the bytes the server sent.

## The procedure

1. **Read the probe line and the warnings.** A redirect, an unverified
   certificate or a wide-mode extraction each change what is to be checked.
2. **Prune.** A web page carries navigation, "[edit]" links, banners, related
   blocks, infoboxes that come out as broken tables. The extraction removes most
   of it but not all. When the tool reports that it had to fall back to **wide**
   mode (the images were missing in precise mode), more remains to cut.
3. **Restore the hierarchy.** The site's headings are not the repository's:
   bring them back to the presets' `##` / `###`. Remove a site suffix from the
   title (`… - Wikipedia`).
4. **Check the images.** Those that failed are listed in `study/meta.json`,
   each with its reason. Each figure arrives titled "Figure — to be captioned":
   caption it or remove it.
5. **Propose the cover** (the `pdf` skill, *The cover*), including the URL and
   the capture date. These are *not* carried by default: they are often useful
   on a web capture, but that is the user's call.
6. **Build and review** (the `pdf` skill, *Build, then review*).

The comment block at the top of `document/index.md` repeats what is left to do for this
page. Delete it once done.

## Options

`make fetch` passes `TO` and `RENDER`. Run directly, the script also takes
`--preset` and `--force`, which overwrites an existing destination:

```bash
.venv/bin/python .claude/skills/fetch/scripts/fetch.py URL watch/article --force
```
