import sys
from pathlib import Path

path = Path(sys.argv[1])
words = [w.strip() for w in path.read_text(encoding="utf-8").splitlines() if w.strip()]
print("Tong so tu:", len(words))
print("Tong so chu Han:", sum(len(w) for w in words))
print()
for i, w in enumerate(words, start=1):
    codes = ",".join(str(ord(c)) for c in w)
    print(f"{i}\t{w}\t{codes}")
