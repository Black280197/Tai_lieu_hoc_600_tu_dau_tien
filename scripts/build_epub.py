#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dựng EPUB 3 từ file Markdown tài liệu Hán tự.

Đặc điểm:
  * Mỗi mục H3 (### N. 字) -> 1 chương riêng  => mục lục điều hướng từng từ.
  * Mục H2 (phần mở đầu / phần tổng kết) -> chương riêng.
  * Tải toàn bộ ảnh bishun.net về và nhúng vào EPUB (đọc offline trên máy đọc sách).
  * CSS tối ưu màn hình E-ink: tương phản cao, không phụ thuộc màu, chống tràn lề.

Cách dùng:
  python scripts/build_epub.py All_words/1_100_chi_tiet.md dist/part1.epub ^
      --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 1" --author "Tài liệu tự biên soạn"
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import markdown
import requests

# --------------------------------------------------------------------------
# CSS tối ưu cho màn hình E-ink (đen trắng, tương phản cao, không tràn lề)
# --------------------------------------------------------------------------
CSS = """@charset "utf-8";

/* ---------- Nền tảng ---------- */
html, body { margin: 0; padding: 0; }

body {
  font-family: "Noto Serif CJK SC", "Songti SC", "SimSun", serif;
  font-size: 1em;
  line-height: 1.68;
  color: #000;
  background: #fff;
  text-align: justify;
  -webkit-hyphens: auto;
  hyphens: auto;
  widows: 2;
  orphans: 2;
}

/* ---------- Tiêu đề ---------- */
h1 {
  font-size: 1.55em;
  line-height: 1.35;
  text-align: center;
  margin: 1.4em 0 0.5em;
  page-break-after: avoid;
  break-after: avoid;
}

h2 {
  font-size: 1.22em;
  line-height: 1.4;
  margin: 1.5em 0 0.6em;
  padding-bottom: 0.25em;
  border-bottom: 2px solid #000;
  page-break-after: avoid;
  break-after: avoid;
}

h3 {
  font-size: 1.18em;
  line-height: 1.4;
  margin: 1.1em 0 0.7em;
  padding: 0.22em 0.5em;
  border-left: 5px solid #000;
  page-break-after: avoid;
  break-after: avoid;
}

/* ---------- Đoạn văn & danh sách ---------- */
p { margin: 0.38em 0; text-indent: 0; }

ul, ol {
  margin: 0.35em 0 0.7em;
  padding-left: 1.15em;
}

li { margin: 0.28em 0; }

li > ul, li > ol { margin: 0.2em 0 0.25em; }

/* ---------- Khối trích dẫn: khung nổi bật, an toàn cho E-ink ---------- */
blockquote {
  margin: 0.9em 0;
  padding: 0.65em 0.85em;
  border: 1px solid #000;
  border-left: 6px solid #000;
  background: #f2f2f2;
  font-style: italic;
  page-break-inside: avoid;
  break-inside: avoid;
}

blockquote p { margin: 0; }

/* ---------- Ảnh thứ tự nét ---------- */
img {
  max-width: 60%;
  height: auto;
  display: block;
  margin: 10px auto;
  page-break-inside: avoid;
  break-inside: avoid;
}

/* ---------- Đường phân cách ---------- */
hr {
  border: 0;
  border-top: 1px solid #000;
  margin: 1em 0;
}

/* ---------- Chữ nhấn mạnh ---------- */
strong { font-weight: bold; }
em { font-style: italic; }

/* ---------- Mục lục ---------- */
nav#toc ol { list-style-type: none; padding-left: 0.9em; }
nav#toc li { margin: 0.32em 0; line-height: 1.4; }

/* ---------- Ngắt trang ---------- */
.newpage { page-break-before: always; break-before: page; }
"""

# Cho phép tuỳ biến CSS từ bên ngoài: styles/eink.css (nếu tồn tại)
_EXTERNAL_CSS = Path(__file__).resolve().parent.parent / "styles" / "eink.css"
if _EXTERNAL_CSS.exists():
    CSS = _EXTERNAL_CSS.read_text(encoding="utf-8")

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="vi" lang="vi">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
{body}
</body>
</html>
"""

CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def split_sections(text: str):
    """Tách văn bản thành các khối: phần mở đầu, từng mục H3, mục H2 phía sau."""
    intro: list[str] = []
    sections: list[dict] = []
    current: dict | None = None

    for line in text.splitlines():
        if line.startswith("### "):
            if current is None:
                pass  # dòng mở đầu rỗng, bỏ
            current = {"level": 3, "title": line[4:].strip(), "lines": [line]}
            sections.append(current)
        elif line.startswith("## ") and sections:
            current = {"level": 2, "title": line[3:].strip(), "lines": [line]}
            sections.append(current)
        else:
            if current is None:
                intro.append(line)
            else:
                current["lines"].append(line)

    return "\n".join(intro).strip(), sections


def md_to_html(text: str) -> str:
    md = markdown.Markdown(
        output_format="xhtml",
        extensions=["extra", "sane_lists", "md_in_html"],
        tab_length=2,
    )
    return md.convert(text).strip()


def nav_label(title: str, body_md: str) -> str:
    """Nhãn mục lục: '1. 一 — yī'."""
    m = re.search(r"\*\*Pinyin:\*\*\s*([^\n*]+)", body_md)
    pinyin = ""
    if m:
        pinyin = m.group(1).strip().rstrip(".")
        pinyin = re.split(r"[;；]", pinyin)[0].strip()
        if len(pinyin) > 22:
            pinyin = pinyin[:22] + "…"
    label = title
    if pinyin:
        label = f"{title} — {pinyin}"
    return label


IMG_RE = re.compile(r'src="(https?://[^"]+?/bishun-(\d+)\.png)"')


def download_images(text: str, cache_dir: Path, timeout: int = 25):
    """Tải ảnh về cache, trả về (text_đã_thay, dict code->file)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    found = {code for _, code in IMG_RE.findall(text)}
    saved: dict[str, Path] = {}
    ok = fail = 0

    for code in sorted(found):
        dest = cache_dir / f"bishun-{code}.png"
        if dest.exists() and dest.stat().st_size > 0:
            saved[code] = dest
            ok += 1
            continue
        url = f"https://bishun.net/assets/bishun/fenbu/bishun-{code}.png"
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n":
                dest.write_bytes(r.content)
                saved[code] = dest
                ok += 1
            else:
                fail += 1
                print(f"  [canh bao] Khong tai duoc {url} (HTTP {r.status_code})", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            fail += 1
            print(f"  [canh bao] Loi tai {url}: {exc}", file=sys.stderr)

    def repl(m: re.Match) -> str:
        code = m.group(2)
        if code in saved:
            return f'src="images/bishun-{code}.png"'
        return m.group(0)  # giữ URL gốc nếu tải thất bại

    return IMG_RE.sub(repl, text), saved, ok, fail


def build(md_path: Path, out_path: Path, title: str, author: str, cache_dir: Path):
    global uid, modified
    if not isinstance(globals().get("uid"), str):
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, title))
    if not isinstance(globals().get("modified"), str):
        modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    raw = md_path.read_text(encoding="utf-8")
    intro_md, sections = split_sections(raw)
    if not sections:
        sys.exit("Khong tim thay muc nao (### ...) trong file.")

    print(f"  Tim thay {len(sections)} muc.")

    # Tải ảnh trước (trên toàn văn bản, để cache dùng chung)
    raw, images, ok, fail = download_images(raw, cache_dir)
    print(f"  Anh: {ok} tai thanh cong, {fail} that bai.")

    # Tách lại sau khi đã đổi đường dẫn ảnh
    intro_md, sections = split_sections(raw)

    chapters = []  # (filename, title_nav, xhtml, etype)

    # --- Trang đầu ---
    if intro_md:
        h1 = next((l[2:].strip() for l in intro_md.splitlines() if l.startswith("# ")), title)
        body = md_to_html(intro_md)
        chapters.append(("c000.xhtml", h1, XHTML.format(title=escape(h1), body=body), "frontmatter"))
        intro_label = h1
    else:
        intro_label = None

    # --- Các mục nội dung ---
    for i, sec in enumerate(sections, start=1):
        body_md = "\n".join(sec["lines"]).strip()
        body = md_to_html(body_md)
        label = nav_label(sec["title"], body_md) if sec["level"] == 3 else sec["title"]
        etype = "chapter" if sec["level"] == 3 else "conclusion"
        fname = f"c{i:03d}.xhtml"
        chapters.append((fname, label, XHTML.format(title=escape(sec["title"]), body=body), etype))

    # --- nav.xhtml ---
    items = "\n".join(
        f'      <li><a href="{fn}">{escape(lbl)}</a></li>' for fn, lbl, _, et in chapters
    )
    nav_body = (
        '<nav epub:type="toc" id="toc">\n'
        "  <h2>Mục lục</h2>\n"
        "  <ol>\n"
        f"{items}\n"
        "  </ol>\n"
        "</nav>\n"
        '<nav epub:type="landmarks" id="landmarks" hidden="hidden">\n'
        "  <ol>\n"
        f'    <li><a epub:type="toc" href="nav.xhtml">Mục lục</a></li>\n'
        f'    <li><a epub:type="bodymatter" href="{chapters[1][0] if len(chapters) > 1 else chapters[0][0]}">Bắt đầu nội dung</a></li>\n'
        "  </ol>\n"
        "</nav>"
    )
    nav_xhtml = XHTML.format(title="Mục lục", body=nav_body)

    # --- toc.ncx (tương thích EPUB2) ---
    points = []
    for i, (fn, lbl, _, _) in enumerate(chapters, start=1):
        points.append(
            f'    <navPoint id="np{i}" playOrder="{i}">\n'
            f"      <navLabel><text>{escape(lbl)}</text></navLabel>\n"
            f'      <content src="{fn}"/>\n'
            "    </navPoint>"
        )
    toc_ncx = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="vi">\n'
        "  <head>\n"
        f'    <meta name="dtb:uid" content="urn:uuid:{uid}"/>\n'
        '    <meta name="dtb:depth" content="1"/>\n'
        '    <meta name="dtb:totalPageCount" content="0"/>\n'
        '    <meta name="dtb:maxPageNumber" content="0"/>\n'
        "  </head>\n"
        f"  <docTitle><text>{escape(title)}</text></docTitle>\n"
        "  <navMap>\n" + "\n".join(points) + "\n  </navMap>\n</ncx>\n"
    )

    # --- content.opf ---
    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '    <item id="css" href="style.css" media-type="text/css"/>',
    ]
    for i, (fn, _, _, _) in enumerate(chapters):
        manifest.append(
            f'    <item id="ch{i}" href="{fn}" media-type="application/xhtml+xml"/>'
        )
    for code, path in sorted(images.items()):
        manifest.append(
            f'    <item id="img{code}" href="images/bishun-{code}.png" media-type="image/png"/>'
        )
    spine = "\n".join(f'    <itemref idref="ch{i}"/>' for i in range(len(chapters)))

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="vi">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:{uid}</dc:identifier>
    <dc:title>{escape(title)}</dc:title>
    <dc:language>vi</dc:language>
    <dc:creator>{escape(author)}</dc:creator>
    <dc:description>Tài liệu học Hán tự theo phương pháp chiết tự và tự nguyên.</dc:description>
    <meta property="dcterms:modified">{modified}</meta>
  </metadata>
  <manifest>
{chr(10).join(manifest)}
  </manifest>
  <spine toc="ncx">
{spine}
  </spine>
</package>
"""

    # --- Ghi file EPUB ---
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as z:
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/epub+zip")

        z.writestr("META-INF/container.xml", CONTAINER, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav_xhtml, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", toc_ncx, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)

        for fn, _, html, _ in chapters:
            z.writestr(f"OEBPS/{fn}", html, compress_type=zipfile.ZIP_DEFLATED)

        for code, path in sorted(images.items()):
            z.write(path, f"OEBPS/images/bishun-{code}.png", compress_type=zipfile.ZIP_STORED)

    size = out_path.stat().st_size / 1024
    print(f"  => {out_path}  ({size:,.0f} KB, {len(chapters)} chuong, {len(images)} anh)")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Dựng EPUB 3 từ Markdown Hán tự")
    ap.add_argument("markdown_file")
    ap.add_argument("output_epub")
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", default="Tài liệu tự biên soạn")
    ap.add_argument("--cache", default=".cache/bishun", help="Thư mục cache ảnh")
    args = ap.parse_args()

    md_path = Path(args.markdown_file)
    out_path = Path(args.output_epub)
    if not md_path.exists():
        sys.exit(f"Khong tim thay file: {md_path}")

    # Các biến dùng trong opf/toc (build() cũng tự khởi tạo nếu chưa có)
    global uid, modified
    uid = str(uuid.uuid5(uuid.NAMESPACE_URL, args.title))
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[EPUB] {md_path} -> {out_path}")
    build(md_path, out_path, args.title, args.author, Path(args.cache))


if __name__ == "__main__":
    main()
