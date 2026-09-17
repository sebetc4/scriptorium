# Manipulating an existing PDF

Loaded on demand. The skill's main work is building documents; this file covers
the few operations on an already-made PDF that a library of documents actually
needs: assembling, splitting, reading its text, pulling its images, rendering
its pages.

Written for this repository, not copied from anywhere. Every recipe uses a
library `requirements.txt` already pins and runs through `.venv/bin/python`
from the repository root. None of them needs a system tool.

| Need | Library | Why this one |
|---|---|---|
| Merge, split, reorder, metadata | `pypdf` | pure Python, writes PDFs |
| Text with its layout, images | `pymupdf` | what `ingest.py` already reads with |
| A page as an image | `core.pdfpage` | the shared brick over `pypdfium2`; never call `pypdfium2` directly |

**Which operations are here.** One test decides it: *can a document of this
library ever be the subject of the operation?* Assembling several built PDFs,
extracting a page range to send, reading an imported source — yes. Filling a
form, encrypting, OCR on a scan, drawing a PDF by hand with a canvas API — no:
nothing here is a form or a scan, and a PDF is made by `make build`, never drawn.

---

## Merge

```python
from pypdf import PdfWriter

writer = PdfWriter()
for path in ["out/pdf/a/a.pdf", "out/pdf/b/b.pdf"]:
    writer.append(path)
writer.write("merged.pdf")
```

`append` also takes `pages=(start, stop)`, zero-based and stop-exclusive, to
take only part of a file.

Merge **built outputs**, never sources: if the result is meant to last, it
should be one document under `library/` with one `index.md`, built once.

## Split, or extract a page range

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("in.pdf")
writer = PdfWriter()
for page in reader.pages[2:5]:          # pages 3 to 5
    writer.add_page(page)
writer.write("pages-3-5.pdf")
```

One file per page: the same loop, one `PdfWriter` per page.

## Metadata

```python
from pypdf import PdfReader

meta = PdfReader("in.pdf").metadata or {}
print(meta.get("/Title"), meta.get("/Author"), meta.get("/Producer"))
```

A PDF built here takes its title and author from the front matter. To change
them, change the front matter and rebuild. Do not patch the output.

## Text

```python
import pymupdf

with pymupdf.open("in.pdf") as pdf:
    for number, page in enumerate(pdf, start=1):
        text = page.get_text()
        if not text.strip():
            print(f"page {number}: no text layer")
```

`page.get_text("dict")` returns the blocks, lines and spans with their font,
size and flags. That is how `ingest.py` recovers headings and emphasis. To
**rebuild** a PDF as a document, do not reimplement this: run `make import`.

A page with no text layer is a scan or a drawing. OCR is not part of this
skill, and a page like that is redrawn or described rather than recognised.

## Images

```python
import pymupdf

with pymupdf.open("in.pdf") as pdf:
    for number, page in enumerate(pdf, start=1):
        for index, info in enumerate(page.get_images(full=True)):
            image = pdf.extract_image(info[0])
            name = f"p{number}-{index}.{image['ext']}"
            open(name, "wb").write(image["image"])
```

This yields the raster images as they were embedded. Vector drawings are not
images and do not come out: that is why `make import` names the pages that
carry one, to be redrawn with `diagram-design`.

## A page as an image

```python
from pathlib import Path
from core import pdfpage

for i, image in enumerate(pdfpage.render(Path("in.pdf"), scale=2)):
    image.save(f"page-{i + 1:02d}.png")
```

`scale` multiplies the page's own size in points; `width_px=` targets a pixel
width instead, which keeps pages of different sizes at the same width. Exactly
one of the two. `pdfpage.first()` renders only the first page.

This is the review loop's brick (see `SKILL.md`, *Build, then review*), and the
EPUB backbone and the review sheets use the same one.
