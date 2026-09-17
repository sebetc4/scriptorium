"""contact_sheet.py: one look at a folder of images, or at a PDF's pages."""
from PIL import Image
from weasyprint import HTML

import contact_sheet


def images(folder, n):
    folder.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        Image.new("RGB", (800, 600), (i * 10 % 255, 80, 120)).save(folder / f"IMG_{i:04d}.jpg")
    return folder


def test_a_folder_becomes_one_sheet(tmp_path, capsys):
    src = images(tmp_path / "repair", 6)
    out = tmp_path / "sheet.png"
    assert contact_sheet.main([str(src), "-o", str(out)]) == 0
    sheet = Image.open(out)
    assert sheet.width == 4 * contact_sheet.CELL[0]
    assert str(out) in capsys.readouterr().out


def test_files_that_are_not_images_are_skipped_and_named(tmp_path, capsys):
    src = images(tmp_path / "repair", 2)
    (src / "notes.txt").write_text("not an image")
    (src / "broken.jpg").write_bytes(b"<!DOCTYPE html><title>404</title>")
    assert contact_sheet.main([str(src), "-o", str(tmp_path / "s.png")]) == 0
    out = capsys.readouterr().out
    assert "broken.jpg" in out
    assert "notes.txt" not in out       # not an image by its name: silently ignored


def test_a_large_folder_is_split_across_sheets(tmp_path, capsys):
    src = images(tmp_path / "teardown", contact_sheet.PER_SHEET + 3)
    out = tmp_path / "sheet.png"
    assert contact_sheet.main([str(src), "-o", str(out)]) == 0
    assert (tmp_path / "sheet-01.png").is_file()
    assert (tmp_path / "sheet-02.png").is_file()
    assert not out.exists()


def test_a_pdf_becomes_a_sheet_of_its_pages(tmp_path):
    pdf = tmp_path / "manual.pdf"
    HTML(string="<p>one</p><p style='break-before:page'>two</p>"
                "<p style='break-before:page'>three</p>").write_pdf(pdf)
    out = tmp_path / "pages.png"
    assert contact_sheet.main([str(pdf), "-o", str(out)]) == 0
    assert Image.open(out).width == 4 * contact_sheet.CELL[0]


def test_a_page_range_limits_the_pdf(tmp_path):
    pdf = tmp_path / "manual.pdf"
    HTML(string="".join(f"<p style='break-before:page'>{i}</p>" for i in range(6))).write_pdf(pdf)
    out = tmp_path / "pages.png"
    assert contact_sheet.main([str(pdf), "--pages", "2-3", "-o", str(out)]) == 0
    assert Image.open(out).height == contact_sheet.CELL[1]


def test_a_folder_with_no_image_fails_loudly(tmp_path, capsys):
    (tmp_path / "empty").mkdir()
    (tmp_path / "empty" / "readme.txt").write_text("x")
    assert contact_sheet.main([str(tmp_path / "empty"), "-o", str(tmp_path / "s.png")]) == 1
    assert "no image" in capsys.readouterr().err
    assert not (tmp_path / "s.png").exists()


def test_a_folder_of_unreadable_images_fails_loudly(tmp_path, capsys):
    (tmp_path / "walls").mkdir()
    for name in ("a.jpg", "b.jpg"):
        (tmp_path / "walls" / name).write_bytes(b"<!DOCTYPE html>")
    assert contact_sheet.main([str(tmp_path / "walls"), "-o", str(tmp_path / "s.png")]) == 1
    assert "no image" in capsys.readouterr().err
