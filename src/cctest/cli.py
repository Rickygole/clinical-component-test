import argparse
import json
import sys

from . import agreement, layers
from .agreement import InputError


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cctest")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("agreement", help="agreement test for combined language models")
    a.add_argument("input")
    a.add_argument("--models", required=True, help="comma separated model_id values")
    a.add_argument("--permutations", type=int, default=10000)
    a.add_argument("--seed", type=int, default=42)
    l = sub.add_parser("layers", help="data-layer test for multi-input fusion models")
    l.add_argument("folds")
    l.add_argument("--oof")
    l.add_argument("--seed", type=int, default=2026)
    for p in (a, l):
        p.add_argument("--limits", help="JSON file of acceptable limits and the date they were recorded")
        p.add_argument("--out", help="write the report here instead of stdout")
    args = ap.parse_args(argv)
    try:
        limits = json.load(open(args.limits)) if args.limits else None
        if args.cmd == "agreement":
            rep = agreement.run(args.input, args.models.split(","), limits, args.permutations, args.seed)
        else:
            rep = layers.run(args.folds, args.oof, limits, args.seed)
    except (InputError, OSError, ValueError) as e:
        print(f"input rejected: {e}", file=sys.stderr)
        return 2
    text = json.dumps(rep, indent=2)
    if args.out:
        open(args.out, "w").write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
