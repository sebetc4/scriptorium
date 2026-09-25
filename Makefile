PY      := .venv/bin/python
PIP     := .venv/bin/pip
DOC     ?=
SRC     ?=
URL     ?=
TO      ?=
RENDER  ?=
VARIANT ?=
ZOOM    ?=
PRESET  ?= report
Q       ?=
IN      ?=
TEXT    ?=
AT      ?=
ID      ?=
L       ?=
TITLE   ?=

.PHONY: help setup brand icons new import fetch build epub watch test check-library list find ls links path clean check preview preview-style review

help:
	@echo "Targets:"
	@echo "  make setup                                  install the environment"
	@echo "  make brand                                  propagate brand/tokens.yaml (CSS + diagram-design)"
	@echo "  make icons [V=1.41.0]                       reinstall the Lucide icon set"
	@echo "  make new DOC=topic/slug [PRESET=] [TITLE=]   create a document"
	@echo "  make import SRC=x.pdf DOC=topic/slug TO=fr   import an external PDF"
	@echo "  make fetch URL=https://… DOC=topic/slug [TO=] [RENDER=1]  capture a web page"
	@echo "  make build [DOC=topic/slug]                 build one document or the whole library"
	@echo "  make review DOC=topic/slug [VARIANT=] [ZOOM=\"3 7\"]  checks + page sheets of a built PDF"
	@echo "  make epub [DOC=topic/slug]                  build one EPUB or all of them"
	@echo "  make preview [DOC=topic/slug]               contact sheet (what does not reflow)"
	@echo "  make preview-style                          style proof (the whole style guide)"
	@echo "  make watch [DOC=topic/slug]                 rebuild on every change"
	@echo "  make rederive DOC=topic/slug                re-extract study/extracted.md from sources/"
	@echo "  make list                                   list the documents"
	@echo "  make find Q=\"words\" [IN=topic] [TEXT=1]     what the library holds about it"
	@echo "  make ls [AT=topic/slug] [L=1|2]             a topic's entries, an entry's items"
	@echo "  make links AT=topic/slug                    what an entry cites, and what cites it"
	@echo "  make path ID=manuel-k7m3p2x9                where an id is"
	@echo "  make test                                   run the tests (never reads library/)"
	@echo "  make check-library                          check the library's documents, writing nothing"
	@echo "  make clean [DOC=topic/slug]                 remove out/ and the documents' .work/"
	@echo ""
	@echo "Presets: $(patsubst theme/%.css,%,$(filter-out theme/base.css theme/page.css theme/code.css,$(wildcard theme/*.css)))"

setup: .venv/bin/python
	@$(PIP) install -q -r requirements.txt
	@$(PIP) install -q -e .
	@$(MAKE) --no-print-directory brand
	@echo "environment ready"

.venv/bin/python:
	@python3 -m venv .venv
	@$(PIP) install -q --upgrade pip

brand:
	@$(PY) brand/sync.py

icons:
	@$(PY) brand/icons.py $(V)

new:
	@test -n "$(DOC)" || { echo "usage: make new DOC=topic/slug [PRESET=report] [TITLE=\"…\"]"; exit 1; }
	@$(PY) .claude/skills/pdf/scripts/new.py "$(DOC)" --preset "$(PRESET)" $(if $(TITLE),--title "$(TITLE)")

# TO rather than LANG: LANG is a standard environment variable, which make
# inherits — it would hold “fr_FR.UTF-8” and not “fr”.
import:
	@test -n "$(SRC)" -a -n "$(DOC)" -a -n "$(TO)" || { echo "usage: make import SRC=source.pdf DOC=topic/slug TO=fr"; exit 1; }
	@$(PY) .claude/skills/pdf/scripts/ingest.py "$(SRC)" "$(DOC)" --lang "$(TO)" $(IMPORT_FLAGS)

fetch:
	@test -n "$(URL)" -a -n "$(DOC)" || { echo "usage: make fetch URL=https://… DOC=topic/slug [TO=fr] [RENDER=1]"; exit 1; }
	@$(PY) .claude/skills/fetch/scripts/fetch.py "$(URL)" "$(DOC)" $(if $(TO),--lang "$(TO)") $(if $(RENDER),--render)

build:
	@$(PY) .claude/skills/pdf/scripts/build.py $(DOC)

# The look at a built PDF, made cheap: text-layer checks, then the pages four to
# an image; ZOOM renders chosen pages alone at full resolution instead.
review:
	@test -n "$(DOC)" || { echo "usage: make review DOC=topic/slug [VARIANT=light|dark] [ZOOM=\"3 7\"]"; exit 1; }
	@$(PY) .claude/skills/pdf/scripts/review.py "$(DOC)" $(if $(VARIANT),--variant $(VARIANT)) $(if $(ZOOM),--zoom $(ZOOM))

# A separate target from `build`: a PDF gets built dozens of times while a
# document is being brought up to standard, and rasterising twelve diagrams on
# every pass would be a gratuitous slowdown.
epub:
	@$(PY) .claude/skills/epub/scripts/epub.py $(DOC)

preview:
	@$(PY) .claude/skills/epub/scripts/preview.py $(DOC)

preview-style:
	@$(PY) .claude/skills/epub/scripts/preview.py --style

watch:
	@$(PY) .claude/skills/pdf/scripts/build.py --watch $(DOC)

# --html keeps the intermediate HTML: useful for debugging the CSS cascade
check:
	@$(PY) .claude/skills/pdf/scripts/build.py --html $(DOC)

test:
	@$(PY) -m pytest -q

# The user's library, checked on request: anatomy, layout, and what the build
# would refuse. Read-only — nothing is built — and never part of `make test`,
# which reads only the suite's own fixtures.
check-library:
	@$(PY) -m core.library

# The library's map, read from its manifests (core/navigate.py). Read-only;
# every answer is 20 lines at most. The agent calls .venv/bin/catalogue.
find:
	@test -n "$(Q)" || { echo 'usage: make find Q="words" [IN=topic/slug] [TEXT=1]'; exit 1; }
	@$(PY) -m core.catalogue find $(Q) $(if $(IN),--in "$(IN)") $(if $(TEXT),--text)

ls:
	@$(PY) -m core.catalogue ls $(if $(AT),"$(AT)") $(if $(filter 1,$(L)),-l) $(if $(filter 2,$(L)),-ll)

links:
	@test -n "$(AT)" || { echo "usage: make links AT=topic/slug (or an id)"; exit 1; }
	@$(PY) -m core.catalogue links "$(AT)"

path:
	@test -n "$(ID)" || { echo "usage: make path ID=manuel-k7m3p2x9"; exit 1; }
	@$(PY) -m core.catalogue path "$(ID)"

list:
	@find library -path '*/document/index.md' -printf '%h\n' 2>/dev/null | sed 's|^library/||;s|/document$$||' | sort || true

# Re-derive what a tool computed from `sources/`, without touching what was
# received, what was written since, or the provenance nothing recomputes. Each
# script decides whether the document is its own and says nothing when it is
# not, so no dispatch logic lives here.
rederive:
	@test -n "$(DOC)" || { echo "usage: make rederive DOC=topic/slug"; exit 1; }
	@$(PY) .claude/skills/pdf/scripts/ingest.py --rederive "$(DOC)"
	@$(PY) .claude/skills/fetch/scripts/fetch.py --rederive "$(DOC)"

clean:
	@$(PY) -c "import sys; from core.doc import clean, ROOT; [print('removed', p.relative_to(ROOT)) for p in clean(sys.argv[1:] or None)]" $(DOC)
