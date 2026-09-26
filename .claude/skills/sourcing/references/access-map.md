# Access map — closed doors, open doors

**Maintained.** Update it whenever an investigation meets a wall or a door not
listed here, with the date. Unlike a site's extraction regex, this knowledge
stays true long enough to be worth keeping, and reading it first saves dozens
of blind requests.

It holds what serves any investigation: platforms, archives, search engines.
What only serves one subject — the sites of one field, one maker's forum — goes
to that investigation's `NOTES.md`, in the library.

Each entry is an observation, dated, not a guarantee: a door can close, a wall
can open. When an entry turns out to be wrong, correct it and date the
correction rather than deleting the old line.

---

## Closed doors

| Target | Behaviour | Seen |
|---|---|---|
| **Reddit** | 403 on `www`, `old`, `api`, `.json` and `.rss`, even with a browser user agent; no Wayback capture of the thread sought. **Treat as unreachable.** | 2026-09-12 · 403 on `/r/…/.json` confirmed 2026-09-13 |
| Document-hosting sites — manualzz, scribd | signup wall or 403 | 2026-09-12 |
| A shop's direct PDF link | answers HTML in HTTP 200 — `fetch_checked.py` rejects it | 2026-09-12 |
| DuckDuckGo HTML | 202 and a challenge page | 2026-09-12 |
| A phpBB forum gone dead | HTTP 500 on every page (index, `viewtopic`, `viewforum`), the certificate failing verification | 2026-09-12 |
| Wayback `archive.org/wayback/available` | 429 after a few requests — use the CDX index | 2026-09-12 |
| Wayback CDX index | an occasional 503 inside a batch; `wayback.py` retries | 2026-09-13, live verification of the tools |

## Open doors

| Need | What works | Seen |
|---|---|---|
| A maker's document | **The maker's own site, directly**, where aggregators refuse. Failing that, an obscure mirror can serve what five aggregators refused — `fetch_checked.py` tries the chain and stops at the first that really serves a PDF. | 2026-09-12 |
| A Discourse forum | the thread's `.json` endpoint — `html2text.py` tries it first. It answered where the site's HTML pages gave 403. | 2026-09-12 · confirmed 2026-09-13 |
| The content of a dead page | the Wayback Machine, through CDX (`wayback.py`) | 2026-09-12 |
| A dead phpBB forum's topic ids | its archived `viewforum.php` listings (`forum_index.py`) — topic pages (`t=`) are archived, message permalinks (`p=`) are not | 2026-09-12 · confirmed 2026-09-13 |
| An Imgur album | the public API (`imgur_album.py`); the page itself cites one image | 2026-09-12 · confirmed 2026-09-13 |
| The indexed content of a dead page | a web search returns what the engine indexed even when the page answers 500. **Second-hand rendering, never a piece**: a lead to follow, not a source to cite. | 2026-09-12 |

## The principle

**When a piece cannot be found, look for the same information elsewhere rather
than insisting on the closed door.** A document that was never published often
has a published relative — another model of the same family, an earlier
edition — that holds the same answer.
