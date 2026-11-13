import csv
import sys
from collections import defaultdict

from cctest.report import wilson


def main(path):
    rows = list(csv.DictReader(open(path), delimiter="\t"))
    by = defaultdict(list)
    for r in rows:
        by[r["configuration"]].append(int(r["flag"]))
    total = sum(sum(v) for v in by.values())
    n = sum(len(v) for v in by.values())
    for name, v in by.items():
        p, lo, hi = wilson(sum(v), len(v))
        print(f"{name}\t{sum(v)}/{len(v)}\t{p * 100:.1f}%\t{lo * 100:.1f} to {hi * 100:.1f}%")
    p, lo, hi = wilson(total, n)
    print(f"pooled\t{total}/{n}\t{p * 100:.1f}%\t{lo * 100:.1f} to {hi * 100:.1f}%")


if __name__ == "__main__":
    main(sys.argv[1])
