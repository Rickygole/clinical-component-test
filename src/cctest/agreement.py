import csv
from collections import Counter, defaultdict

import numpy as np

from .report import entry, report, wilson

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
REQUIRED = ("case_id", "model_id", "answer", "reference_answer", "n_options")


class InputError(ValueError):
    pass


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in REQUIRED if rows and c not in rows[0]]
    if not rows or missing:
        raise InputError(f"{path}: empty file or missing columns {missing}")
    seen = Counter((r["case_id"], r["model_id"]) for r in rows)
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups:
        raise InputError(f"{len(dups)} duplicated (case_id, model_id) pairs, first: {next(iter(dups))}")
    cases = defaultdict(dict)
    ref = {}
    nopt = {}
    for line, r in enumerate(rows, start=2):
        if any(r.get(k) is None for k in REQUIRED):
            raise InputError(f"{path} line {line}: row has fewer fields than the header")
        c = r["case_id"]
        try:
            k = int(r["n_options"])
        except ValueError:
            raise InputError(f"{path} line {line}: n_options must be an integer, got {r['n_options']!r}")
        if not 2 <= k <= len(LETTERS):
            raise InputError(f"{path} line {line}: n_options must be between 2 and {len(LETTERS)}, got {k}")
        gold = r["reference_answer"].strip().upper()
        cases[c][r["model_id"].strip()] = r["answer"].strip().upper()
        if ref.setdefault(c, gold) != gold:
            raise InputError(f"case {c}: models disagree on reference_answer")
        if nopt.setdefault(c, k) != k:
            raise InputError(f"case {c}: models disagree on n_options")
    return cases, ref, nopt


class Panel:
    def __init__(self, cases, ref, nopt, models):
        models = [m.strip() for m in models]
        if len(models) < 2 or len(set(models)) != len(models):
            raise InputError(f"need at least two distinct model ids, got {models}")
        cover = {m: sum(1 for c in cases.values() if m in c) for m in models}
        if len(set(cover.values())) != 1 or cover[models[0]] != len(cases):
            raise InputError(f"unequal coverage across models: {cover} of {len(cases)} cases")
        ids = sorted(cases)
        self.models = list(models)
        self.n_cases = len(ids)
        self.ref = np.array([ref[c] for c in ids])
        self.nopt = np.array([nopt[c] for c in ids])
        self.ans = np.array([[cases[c][m] for m in models] for c in ids])
        valid = np.array([[a != "" and a in LETTERS[:k] for a in row] for row, k in zip(self.ans, self.nopt)])
        refok = np.array([r in LETTERS[:k] for r, k in zip(self.ref, self.nopt)])
        self.valid = valid & refok[:, None]
        self.scored = valid.all(axis=1) & refok
        self.correct = self.ans == self.ref[:, None]

    def counts(self):
        s = self.scored
        a, cor = self.ans[s], self.correct[s]
        agree = (a == a[:, :1]).all(axis=1)
        all_wrong = (~cor).all(axis=1)
        return {
            "scored": int(s.sum()),
            "agree": int(agree.sum()),
            "agree_wrong": int((agree & all_wrong).sum()),
            "all_wrong": int(all_wrong.sum()),
        }

    def wrong_dists(self):
        out = []
        for j in range(len(self.models)):
            w = Counter(a for a, ok, v in zip(self.ans[:, j], self.correct[:, j], self.valid[:, j]) if v and not ok)
            out.append(w)
        return out

    def renorm(self, dist, gold, k):
        opts = [l for l in LETTERS[:k] if l != gold]
        tot = sum(dist.get(l, 0) for l in opts)
        return opts, np.array([dist.get(l, 0) / tot if tot else 1 / len(opts) for l in opts])

    def model_chance(self):
        dists = self.wrong_dists()
        s = self.scored & (~self.correct).all(axis=1)
        vals = []
        for g, k in zip(self.ref[s], self.nopt[s]):
            p = np.prod([self.renorm(d, g, k)[1] for d in dists], axis=0)
            vals.append(p.sum())
        return float(np.mean(vals)) if vals else float("nan")

    def naive_chance(self):
        s = self.scored & (~self.correct).all(axis=1)
        k = len(self.models)
        return float(np.mean((1.0 / (self.nopt[s] - 1)) ** (k - 1))) if s.any() else float("nan")

    def permutation_null(self, n_perm=10000, seed=42):
        rng = np.random.default_rng(seed)
        s = self.scored & (~self.correct).all(axis=1)
        a = self.ans[s]
        if a.shape[0] == 0:
            return np.array([np.nan])
        key = np.array([f"{g}|{k}" for g, k in zip(self.ref[s], self.nopt[s])])
        strata = [np.flatnonzero(key == u) for u in np.unique(key)]
        rates = np.empty(n_perm)
        for b in range(n_perm):
            p = a.copy()
            for idx in strata:
                for j in range(1, a.shape[1]):
                    p[idx, j] = a[rng.permutation(idx), j]
            rates[b] = (p == p[:, :1]).all(axis=1).mean()
        return rates


def run(path, models, limits=None, n_perm=10000, seed=42, label=None):
    cases, ref, nopt = load(path)
    p = Panel(cases, ref, nopt, models)
    models = p.models
    c = p.counts()
    if c["scored"] == 0:
        raise InputError("no case could be scored: every case has a missing or invalid answer or reference")
    unit = label or f"{len(models)} models: " + ", ".join(models)
    est = {}
    entries = []
    for test, x, n, u in (
        ("agreed_answer_error_rate", c["agree_wrong"], c["agree"], "cases where all models give the same answer"),
        ("unanimous_wrong_rate", c["agree_wrong"], c["all_wrong"], "cases all models answered wrongly"),
        ("agreed_wrong_exposure", c["agree_wrong"], c["scored"], "all scored cases"),
    ):
        e, lo, hi = wilson(x, n)
        est[test] = e
        entries.append(entry(test, f"{unit}; denominator: {u}", e, lo, hi, models, limits, x, n))
    null = p.permutation_null(n_perm, seed)
    empty = bool(np.isnan(null).all())
    null_mean = float("nan") if empty else float(np.nanmean(null))
    p95 = float("nan") if empty else float(np.nanpercentile(null, 95))
    naive = p.naive_chance()
    analytic = p.model_chance()
    obs = est["unanimous_wrong_rate"]
    baselines = {
        "naive_independence": naive,
        "model_expectation": analytic,
        "permutation_mean": null_mean,
        "permutation_95th_percentile": p95,
        "permutation_n": n_perm,
        "permutation_seed": seed,
        "ratio_to_naive": obs / naive if naive else None,
        "ratio_to_model_expectation": obs / analytic if analytic else None,
        "ratio_to_permutation_mean": obs / null_mean if null_mean else None,
    }
    entries[1]["baselines"] = baselines
    flags = []
    if obs > p95:
        flags.append({
            "flag": "convergent_failure",
            "components": models,
            "rule": "unanimous_wrong_rate above the 95th percentile of the permutation baseline",
            "observed": obs,
            "threshold": p95,
        })
    notes = [f"{p.n_cases - c['scored']} of {p.n_cases} cases unscored: at least one missing or invalid answer"]
    return report("agreement", [path], entries, flags, notes)

