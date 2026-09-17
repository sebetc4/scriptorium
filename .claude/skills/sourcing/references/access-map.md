# Access map — closed doors, open doors

**Maintained.** Update it whenever an investigation meets a wall or a door not
listed here, with the date and the investigation. Unlike a site's extraction
regex, this knowledge stays true long enough to be worth keeping, and reading
it first saves dozens of blind requests.

Each entry is an observation, dated, not a guarantee: a door can close, a wall
can open. When an entry turns out to be wrong, correct it and date the
correction rather than deleting the old line.

---

## Closed doors

| Target | Behaviour | Seen |
|---|---|---|
| **Reddit** | 403 on `www`, `old`, `api`, `.json` and `.rss`, even with a browser user agent; no Wayback capture of the thread sought. **Treat as unreachable.** | 2026-09-12, Electribe 2 · 403 on `/r/…/.json` confirmed 2026-09-13 |
| **ModWiggler** | 403, even with a browser user agent | 2026-09-12, Electribe 2 |
| Datasheet aggregators — alldatasheet, datasheetq, datasheetbank, datasheets360, chipfind | systematic 403 | 2026-09-12, Electribe 2 |
| manualzz, elektrotanya, scribd | signup wall or 403 | 2026-09-12, Electribe 2 |
| Mouser, direct PDF link | answers HTML in HTTP 200 — `fetch_checked.py` rejects it | 2026-09-12, Electribe 2 |
| DuckDuckGo HTML | 202 and a challenge page | 2026-09-12, Electribe 2 |
| `korgforums.com/forum/phpBB3/` | HTTP 500 on every page (index, `viewtopic`, `viewforum`); the certificate fails verification | 2026-09-12, Electribe 2 · homepage 200 with an unverified certificate, 2026-09-13 |
| Wayback `archive.org/wayback/available` | 429 after a few requests — use the CDX index | 2026-09-12, Electribe 2 |
| Wayback CDX index | an occasional 503 inside a batch; `wayback.py` retries | 2026-09-13, live verification of the tools |

## Open doors

| Need | What works | Seen |
|---|---|---|
| A component datasheet | **The manufacturer's site, directly**: `assets.nexperia.com/documents/data-sheet/<REF>.pdf`, `sameskydevices.com/product/resource/<ref>.pdf`. Failing that, obscure mirrors — `1688eric.com` served the Sanyo CPH6302 sheet five aggregators refused. | 2026-09-12, Electribe 2 |
| Synthesizer service manuals | **`polynominal.com`** and **`vintagesynthparts.com`** serve PDFs directly, no signup. A first-rank resource for musical electronics. | 2026-09-12, Electribe 2 |
| Manufacturer documentation | the official site, directly — `cdn.korg.com` served a 112-page manual without difficulty | 2026-09-12, Electribe 2 |
| A Discourse forum | the thread's `.json` endpoint — `html2text.py` tries it first. It answered where the site's HTML pages gave 403 (`forums.syntaur.com`). | 2026-09-12, Electribe 2 · confirmed 2026-09-13 |
| The content of a dead page | the Wayback Machine, through CDX (`wayback.py`) | 2026-09-12, Electribe 2 |
| A dead phpBB forum's topic ids | its archived `viewforum.php` listings (`forum_index.py`) — message permalinks are not archived | 2026-09-12, Electribe 2 · `p=699929` still uncaptured, `t=105619` and `t=94641` captured, 2026-09-13 |
| An Imgur album | the public API (`imgur_album.py`); the page itself cites one image | 2026-09-12, Electribe 2 · confirmed 2026-09-13 |
| The indexed content of a dead page | a web search returns what the engine indexed even when the page answers 500. **Second-hand rendering, never a piece**: a lead to follow, not a source to cite. | 2026-09-12, Electribe 2 |

## The principle

**When a piece cannot be found, look for the same information elsewhere rather
than insisting on the closed door.** The Electribe 2 power schematic does not
exist publicly. Those of three other Korg machines of the same family do, and
they hold the part sought, its designator and its pinout.
