"""Chuẩn hoá tài liệu 600 từ theo brain.md mới.

- Thay mục "Bóc tách thành phần từng chữ" bằng phân tích theo thành phần
  (dữ liệu trong data/boc_tach_partN.md, khoá theo STT).
- Dọn các cụm đếm nét còn sót ("ba nét —", "bảy nét", ...).
- Chèn/cập nhật mục "Kiến thức văn hóa & lịch sử" từ data/van_hoa_partN.md.

Chạy: python scripts/rewrite_entries.py [partN ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PARTS = {
    "part1": "All_words/1_100_chi_tiet.md",
    "part2": "All_words/101_200_chi_tiet.md",
    "part3": "All_words/201_300_chi_tiet.md",
    "part4": "All_words/301_400_chi_tiet.md",
    "part5": "All_words/401_500_chi_tiet.md",
    "part6": "All_words/501_600_chi_tiet.md",
}

BOC = "**Bóc tách thành phần từng chữ**"
NGUON_CHU = "**Nguồn gốc & Bản chất từng chữ**"
VAN_HOA = "**Kiến thức văn hóa & lịch sử**"
HINH_ANH = "**Hình ảnh liên tưởng & Câu chuyện ghi nhớ**"

NUM = r"(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|\d+)"


def load_blocks(path: Path) -> dict[int, str]:
    """Đọc file dữ liệu dạng: ## 12 ...nội dung... ## 13 ..."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    pieces = re.split(r"(?m)^##\s+(\d+)\s*$", text)
    out: dict[int, str] = {}
    for i in range(1, len(pieces), 2):
        stt = int(pieces[i])
        body = pieces[i + 1].strip()
        if body:
            out[stt] = body
    return out


def clean_stroke_counts(section: str) -> str:
    """Bỏ cách nói đếm nét, giữ lại tên thành phần."""
    s = section

    # "(ba nét)" / "(3 nét)"
    s = re.sub(rf"\s*\(\s*{NUM}\s+nét\s*\)", "", s)
    # "gồm ba nét —", "với năm nét", "ba nét —", "bảy nét", "5 nét -"
    s = re.sub(rf"\b(?:gồm|với)\s+{NUM}\s+nét\s*(?:[—–-]\s*)?", "", s)
    s = re.sub(rf"(?<![\w]){NUM}\s+nét\b\s*(?:[—–-]\s*)?", "", s)

    # Thống nhất nhãn kể chuyện thành phần.
    s = s.replace("Mối liên hệ nội tại:", "Ghép lại:")

    # Bỏ lời dẫn chiếu, giữ lại phần tóm tắt phía sau.
    s = re.sub(r"(?:Như|xem)\s+mục\s+\d+\s*[—–-]\s*", "", s, flags=re.I)
    s = re.sub(r"(?:Như|xem)\s+mục\s+\d+\.\s*", "", s, flags=re.I)
    s = re.sub(r"\s*\(\s*(?:như|xem)?\s*mục\s+\d+\s*\)", "", s, flags=re.I)

    # Đổi tên nét thành mô tả hình dáng trung tính.
    s = s.replace("Nét ngang", "Đường ngang")
    s = s.replace("Nét dọc", "Đường dọc")
    s = s.replace("Nét sổ", "Đường dọc")
    s = s.replace("Nét xiên", "Đường xiên")
    s = s.replace("Nét phẩy", "Đường xiên")
    s = s.replace("Nét móc", "Phần móc")
    s = s.replace("Nét cong", "Đường cong")
    s = s.replace("Nét 㐅", "Đường chéo 㐅")
    s = s.replace("Nét 一", "Đường ngang")
    s = s.replace("Nét 丨", "Trục dọc")
    s = s.replace("Nét 丿", "Đường xiên")
    s = s.replace("Nét 乚", "Phần móc")
    s = s.replace("Nét 乙", "Phần móc")
    s = s.replace("Nét 卜", "Phần 卜")

    # Giữ nguyên thụt lề khi bỏ nhãn "Nét 1 — ..."
    s = re.sub(r"^(\s*\*\s*)Nét\s+\d+\s*[—–-]\s*", r"\1", s, flags=re.M)
    s = re.sub(r"^(\s*\*\s*)Nét\s+\d+\s*:\s*", r"\1", s, flags=re.M)
    s = re.sub(r"^(\s*\*\s*)Nét\s+\d+\s*[–-]\s*\d+\s*:\s*", r"\1", s, flags=re.M)
    # Mọi "Nét ..." còn lại ở đầu dòng -> "Phần ..."
    s = re.sub(r"^(\s*\*\s*)Nét\s+", r"\1Phần ", s, flags=re.M)
    return s


def replace_section(block: str, heading: str, next_heading: str, body: str) -> str:
    pattern = rf"(?ms)^({re.escape(heading)}\n)(.*?)(?=^{re.escape(next_heading)})"
    repl = lambda m: m.group(1) + "\n" + body.strip() + "\n\n"
    new, n = re.subn(pattern, repl, block, count=1)
    if n != 1:
        raise RuntimeError(f"Không tìm thấy mục {heading}")
    return new


def insert_or_replace_culture(block: str, body: str) -> str:
    body = body.strip()
    if VAN_HOA in block:
        pattern = rf"(?ms)^({re.escape(VAN_HOA)}\n)(.*?)(?=^{re.escape(HINH_ANH)})"
        new, n = re.subn(pattern, lambda m: m.group(1) + "\n" + body + "\n\n", block, count=1)
        if n != 1:
            raise RuntimeError("Không thay được mục văn hoá")
        return new

    marker = f"{VAN_HOA}\n\n{body}\n\n{HINH_ANH}"
    if HINH_ANH not in block:
        raise RuntimeError("Không tìm thấy mục Hình ảnh")
    return block.replace(HINH_ANH, marker, 1)


def process_part(key: str) -> tuple[int, int, list[int], list[int]]:
    md = ROOT / PARTS[key]

    # Gộp mọi file override để không phụ thuộc việc chia part.
    overrides: dict[int, str] = {}
    for path in sorted(DATA.glob("boc_tach*.md")):
        overrides.update(load_blocks(path))

    cultures = load_blocks(DATA / f"van_hoa_{key}.md")
    ghep_fix = load_blocks(DATA / "ghep_fix.md")

    text = md.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)(?=^### )", text)
    changed = 0
    missing_culture: list[int] = []
    missing_override: list[int] = []
    used_override: list[int] = []

    for i, block in enumerate(blocks):
        m = re.match(r"(?m)^###\s+(\d+)\.\s", block)
        if not m:
            continue
        stt = int(m.group(1))

        # 1) Bóc tách thành phần
        if stt in overrides:
            block = replace_section(block, BOC, NGUON_CHU, clean_stroke_counts(overrides[stt]))
            used_override.append(stt)
        else:
            cm = re.search(rf"(?ms)^({re.escape(BOC)}\n)(.*?)(?=^{re.escape(NGUON_CHU)})", block)
            if not cm:
                raise RuntimeError(f"{key} #{stt}: thiếu mục bóc tách")
            before = cm.group(2)
            after = clean_stroke_counts(before)
            if after != before:
                block = block[: cm.start(2)] + after + block[cm.end(2):]

        # 1b) Bổ sung "Ghép lại" nếu mục còn thiếu
        if stt in ghep_fix:
            cm2 = re.search(rf"(?ms)^({re.escape(BOC)}\n)(.*?)(?=^{re.escape(NGUON_CHU)})", block)
            if cm2 and "Ghép lại:" not in cm2.group(2):
                new_sec = cm2.group(2).rstrip() + "\n" + ghep_fix[stt].strip() + "\n\n"
                block = block[: cm2.start(2)] + new_sec + block[cm2.end(2):]

        # 2) Kiến thức văn hoá
        if stt in cultures:
            block = insert_or_replace_culture(block, cultures[stt])
        else:
            missing_culture.append(stt)

        blocks[i] = block
        changed += 1

    md.write_text("".join(blocks), encoding="utf-8")
    return changed, len(used_override), missing_culture, missing_override


def main() -> None:
    keys = sys.argv[1:] or list(PARTS)
    for key in keys:
        changed, n_override, miss_culture, miss_override = process_part(key)
        print(
            f"{key}: {changed} entry | override bóc tách: {n_override} | "
            f"thiếu văn hoá: {len(miss_culture)} | thiếu override: {len(miss_override)}"
        )
        if miss_culture:
            print("  thiếu văn hoá STT:", miss_culture)
        if miss_override:
            print("  thiếu override STT:", miss_override)


if __name__ == "__main__":
    main()
