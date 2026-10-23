import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

bad = []
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s.startswith("**Nét vẽ chữ") and s != "**Nét vẽ chữ (Thứ tự từng nét)**":
        bad.append((i, "heading-netve", s))
    if "bishun.net" in s and "/assets/bishun/fenbu/bishun-" not in s:
        bad.append((i, "img-url", s))
    if "nội tích" in s:
        bad.append((i, "typo-noitich", s))
    if "**Bóc tách thành phần từng nét**" in s:
        bad.append((i, "heading-boctach", s))
    if "**Nguồn gốc & Bản chất từng cụm từ**" in s:
        bad.append((i, "heading-nguongoc", s))

if bad:
    for i, kind, s in bad:
        print(f"{i}\t{kind}\t{s[:110]}")
else:
    print("KHONG CO LOI")
print("---")
print("Tong loi:", len(bad))
