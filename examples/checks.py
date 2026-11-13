import sys

RESULTS = []


def check(label, value, printed, scale=1, known_difference=None):
    decimals = len(printed.split(".")[1]) if "." in printed else 0
    got = f"{value * scale:.{decimals}f}"
    ok = got == printed or (got == "-0." + "0" * decimals and printed == got[1:])
    status = "PASS" if ok else ("DIFF" if known_difference else "FAIL")
    RESULTS.append((status, label, got, printed, known_difference))
    print(f"{status}  {label:<66} got {got:>8}  target {printed:>8}")
    if known_difference and not ok:
        print(f"      {known_difference}")


def finish(name):
    fails = [r for r in RESULTS if r[0] == "FAIL"]
    diffs = [r for r in RESULTS if r[0] == "DIFF"]
    print(f"\n{name}: {len(RESULTS) - len(fails) - len(diffs)} pass, {len(diffs)} documented difference, {len(fails)} fail")
    sys.exit(1 if fails else 0)
