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
TITLE   ?=

.PHONY: help setup brand icons new import fetch build epub watch test list clean check preview preview-style review

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
	@echo "  make test                                   run the tests"
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
