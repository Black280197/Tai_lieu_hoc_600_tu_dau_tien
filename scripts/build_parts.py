"""Dựng các bản EPUB của tài liệu 600 từ — giữ nguyên dấu tiếng Việt trong tiêu đề."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_epub import build  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "bishun"

PARTS = {
    "part1": (
        "All_words/1_100_chi_tiet.md",
        "dist/600_tu_part1_001-100.epub",
        "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 1 (001–100)",
    ),
    "part2": (
        "All_words/101_200_chi_tiet.md",
        "dist/600_tu_part2_101-200.epub",
        "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 2 (101–200)",
    ),
    "part3": (
        "All_words/201_300_chi_tiet.md",
        "dist/600_tu_part3_201-300.epub",
        "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 3 (201–300)",
    ),
    "part4": (
        "All_words/301_400_chi_tiet.md",
        "dist/600_tu_part4_301-400.epub",
        "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 4 (301–400)",
    ),
    "part5": (
        "All_words/401_500_chi_tiet.md",
        "dist/600_tu_part5_401-500.epub",
        "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 5 (401–500)",
    ),
    "part6": (
        "All_words/501_600_chi_tiet.md",
        "dist/600_tu_part6_501-600.epub",
        "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 6 (501–600)",
    ),
}

AUTHOR = "Tài liệu học Hán tự"


def main() -> None:
    keys = sys.argv[1:] or list(PARTS)
    for key in keys:
        md_rel, out_rel, title = PARTS[key]
        build(ROOT / md_rel, ROOT / out_rel, title, AUTHOR, CACHE)


if __name__ == "__main__":
    main()
