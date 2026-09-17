"""The mechanical checks: what actually breaks an EPUB."""
import sys
import xml.etree.ElementTree as ET
import zipfile

from core import doc

import check
import epub


def test_a_well_formed_epub_reports_nothing(repo):
    d = repo / "library" / "electronique" / "components" / "led"
    assert check.validate(epub.build_epub(d)) == []


def test_a_compressed_mimetype_is_reported(tmp_path):
    p = tmp_path / "x.epub"
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip")     # compressed
        z.writestr("META-INF/container.xml", epub.CONTAINER_XML)
    anomalies = check.validate(p)
    assert any("mimetype" in a for a in anomalies)


def test_a_residual_var_is_reported(repo, tmp_path):
    d = repo / "library" / "electronique" / "components" / "led"
    src = epub.build_epub(d)
    target = tmp_path / "damaged.epub"
    with zipfile.ZipFile(src) as src_zip, zipfile.ZipFile(target, "w") as dst_zip:
        for info in src_zip.infolist():
            data = src_zip.read(info.filename)
            if info.filename.endswith(".css"):
                data = b"a { color: var(--accent) }"
            dst_zip.writestr(info, data)
    assert any("var(" in a for a in check.validate(target))


def test_a_missing_image_is_reported(repo, tmp_path):
    d = repo / "library" / "electronique" / "components" / "led"
    src = epub.build_epub(d)
    target = tmp_path / "no-image.epub"
    with zipfile.ZipFile(src) as src_zip, zipfile.ZipFile(target, "w") as dst_zip:
        for info in src_zip.infolist():
            if info.filename.endswith("cover.png"):
                continue
            dst_zip.writestr(info, src_zip.read(info.filename))
    assert any("cover.png" in a for a in check.validate(target))


def test_a_chapter_outside_the_spine_is_reported(repo, tmp_path):
    d = repo / "library" / "electronique" / "components" / "led"
    src = epub.build_epub(d)
    target = tmp_path / "holed-spine.epub"
    with zipfile.ZipFile(src) as src_zip, zipfile.ZipFile(target, "w") as dst_zip:
        for info in src_zip.infolist():
            data = src_zip.read(info.filename)
            if info.filename.endswith("content.opf"):
                data = data.replace(b'<itemref idref="ch02"/>', b"")
            dst_zip.writestr(info, data)
    assert any("ch02" in a for a in check.validate(target))


def test_a_missing_epubcheck_returns_none_without_raising(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "EPUBCHECK", "does-not-exist-at-all")
    assert check.epubcheck(tmp_path / "x.epub") is None


def test_epubcheck_failing_without_a_message_is_reported(tmp_path, monkeypatch):
    """A non-zero return code, with not one message: that is not a success."""
    class SilentResult:
        returncode = 1
        stdout = ""
        stderr = ""

    monkeypatch.setattr(check.shutil, "which", lambda _cmd: "/usr/bin/epubcheck")
    monkeypatch.setattr(check.subprocess, "run",
                        lambda *a, **k: SilentResult())
    anomalies = check.epubcheck(tmp_path / "x.epub")
    assert anomalies


def test_a_missing_opf_and_a_residual_var_are_reported_together(repo, tmp_path):
    """A stylesheet defect must not hide behind a missing OPF: the two have
    nothing to do with each other."""
    d = repo / "library" / "electronique" / "components" / "led"
    src = epub.build_epub(d)
    target = tmp_path / "no-opf-var.epub"
    with zipfile.ZipFile(src) as src_zip, zipfile.ZipFile(target, "w") as dst_zip:
        for info in src_zip.infolist():
            if info.filename == "OEBPS/content.opf":
                continue
            data = src_zip.read(info.filename)
            if info.filename.endswith(".css"):
                data = b"a { color: var(--accent) }"
            dst_zip.writestr(info, data)
    anomalies = check.validate(target)
    assert any("content.opf" in a for a in anomalies)
    assert any("var(" in a for a in anomalies)


def test_an_undeclared_file_is_reported(repo, tmp_path):
    d = repo / "library" / "electronique" / "components" / "led"
    src = epub.build_epub(d)
    target = tmp_path / "ghost-file.epub"
    with zipfile.ZipFile(src) as src_zip, zipfile.ZipFile(target, "w") as dst_zip:
        for info in src_zip.infolist():
            dst_zip.writestr(info, src_zip.read(info.filename))
        dst_zip.writestr("OEBPS/text/ghost.xhtml", "<html/>")
    anomalies = check.validate(target)
    assert any("ghost.xhtml" in a for a in anomalies)


def test_a_real_epub_reports_nothing_despite_the_reciprocal_check(repo):
    """A guard rail: mimetype, container.xml and the OPF itself must not be
    reported as “undeclared” by the reciprocal check."""
    d = repo / "library" / "electronique" / "components" / "led"
    target = epub.build_epub(d)
    assert target.is_relative_to(repo / "out" / "epub")
    assert check.validate(target) == []


def test_a_chapter_image_outside_the_manifest_is_reported(repo, tmp_path):
    """A renamed or misspelt `src` in a chapter moves neither the manifest nor
    the archive listing: only a check that opens the chapter and confronts its
    `src` with the manifest can see it."""
    d = repo / "library" / "electronique" / "components" / "led"
    src = epub.build_epub(d)
    target = tmp_path / "ghost-image.epub"
    with zipfile.ZipFile(src) as src_zip, zipfile.ZipFile(target, "w") as dst_zip:
        for info in src_zip.infolist():
            data = src_zip.read(info.filename)
            if info.filename.endswith(".xhtml") and info.filename.startswith(
                    "OEBPS/text/"):
                data = data.replace(b'src="../images/', b'src="../images/x-')
            dst_zip.writestr(info, data)
    anomalies = check.validate(target)
    assert any("outside the manifest" in a for a in anomalies)


def test_a_real_epub_reports_nothing_for_legitimate_image_references(repo):
    """`../images/…` from a chapter and `images/cover.png` from the cover are
    two different path arithmetics; neither may trigger the check on a healthy
    archive."""
    d = repo / "library" / "electronique" / "components" / "led"
    target = epub.build_epub(d)
    with zipfile.ZipFile(target) as z:
        opf = ET.fromstring(z.read("OEBPS/content.opf"))
        manifest = {i.get("id"): i.get("href")
                    for i in opf.iterfind(".//opf:manifest/opf:item", check.OPF_NS)}
        assert check.image_reference_anomalies(z, z.namelist(), manifest) == []


def test_epubcheck_with_messages_fails_the_document(
        repo, monkeypatch, capsys):
    """An epubcheck that finds problems must fail `make epub`, exactly as the
    internal mechanical checks do."""
    d = repo / "library" / "electronique" / "components" / "led"
    monkeypatch.setattr(epub.check, "epubcheck", lambda p: ["serious RNG problem"])
    monkeypatch.setattr(sys, "argv", ["epub.py", str(d)])
    code = epub.main()
    output = capsys.readouterr()
    assert code == 1
    assert "epubcheck: serious RNG problem" in output.err


def test_a_missing_epubcheck_produces_one_notice_only(
        repo, monkeypatch, capsys):
    """The tool's absence must not read as a silent success: an explicit
    notice must appear, once for the whole batch."""
    d = repo / "library" / "electronique" / "components" / "led"
    monkeypatch.setattr(epub.check, "epubcheck", lambda p: None)
    monkeypatch.setattr(sys, "argv", ["epub.py", str(d)])
    code = epub.main()
    output = capsys.readouterr()
    assert code == 0
    assert output.out.count("epubcheck missing") == 1
