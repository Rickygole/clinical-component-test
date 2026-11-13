import datetime
import hashlib
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from . import __version__

Z95 = 1.959963984540054
SCOPE = ("Results hold only for cases drawn like the labeled set used here. "
         "They are evidence for a developer's decision, not a clinical safety finding.")


def wilson(x, n, z=Z95):
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def auroc(y, s):
    y = np.asarray(y)
    n1 = int(y.sum())
    n0 = y.size - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = rankdata(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def percentile_ci(a):
    return float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))


def resample_indices(seed, n_repeats, n_folds, n_patients=None, b=10000, b_patient=2000):
    rng = np.random.default_rng(seed)
    fold_idx = rng.integers(0, n_repeats * n_folds, size=(b, n_repeats * n_folds))
    rep_idx = rng.integers(0, n_repeats, size=(b, n_repeats))
    pat_idx = rng.integers(0, n_patients, size=(b_patient, n_patients)) if n_patients else None
    return fold_idx, rep_idx, pat_idx


def decide(lower, upper, limit):
    if limit is None:
        return "no limit recorded"
    if math.isnan(lower) or math.isnan(upper):
        return "not estimable (empty denominator)"
    if upper <= limit:
        return "supports reliance"
    if lower > limit:
        return "fails"
    return "inconclusive"


def denominator_needed(x, n, limit, cap=10_000_000):
    if n == 0 or x / n == limit:
        return None
    p = x / n

    def resolved(m):
        _, lo, hi = wilson(p * m, m)
        return hi <= limit or lo > limit

    hi = n
    while not resolved(hi):
        hi *= 2
        if hi > cap:
            return None
    lo = n
    while lo < hi:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if resolved(mid) else (mid + 1, hi)
    return lo

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entry(test, unit, estimate, lower, upper, components, limits, count=None, denominator=None, extra=None):
    spec = (limits or {}).get("limits", {}).get(test)
    limit = spec if spec is None or isinstance(spec, (int, float)) else spec.get("value")
    e = {
        "test": test,
        "unit": unit,
        "components": list(components),
        "count": count,
        "denominator": denominator,
        "estimate": estimate,
        "lower_95": lower,
        "upper_95": upper,
        "acceptable_limit": limit,
        "limit_recorded": (limits or {}).get("recorded") if limit is not None else None,
        "decision": decide(lower, upper, limit),
    }
    if e["decision"] == "inconclusive" and count is not None:
        e["denominator_needed"] = denominator_needed(count, denominator, limit)
    if extra:
        e.update(extra)
    return e


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def report(module, inputs, entries, flags, notes=None):
    return clean({
        "tool": "cctest",
        "tool_version": __version__,
        "module": module,
        "run_date": datetime.date.today().isoformat(),
        "inputs": {Path(p).name: sha256(p) for p in inputs},
        "entries": entries,
        "flags": flags,
        "notes": notes or [],
        "scope": SCOPE,
    })
