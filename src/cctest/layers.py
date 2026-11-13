import csv
from collections import defaultdict

import numpy as np

from .agreement import InputError
from .report import auroc, entry, percentile_ci, report, resample_indices


def read(path, value):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    need = {"model_id", "layer", "condition", "repeat", value} | ({"label", "patient_id"} if value == "probability" else {"fold"})
    if not rows or not need <= set(rows[0]):
        raise InputError(f"{path}: empty file or missing columns {sorted(need - set(rows[0] if rows else []))}")
    bad = {r["condition"] for r in rows} - {"with", "without", "solo"}
    if bad:
        raise InputError(f"{path}: unknown condition values {sorted(bad)}")
    return rows


def grid(rows, inner):
    g = defaultdict(dict)
    for r in rows:
        if any(v is None for v in r.values()):
            raise InputError(f"row has fewer fields than the header: {r}")
        k = (r["model_id"], r["layer"], r["condition"])
        try:
            cell = (int(r["repeat"]), r[inner])
        except ValueError:
            raise InputError(f"repeat must be an integer, got {r['repeat']!r}")
        if cell in g[k]:
            raise InputError(f"duplicate row {k} {cell}")
        g[k][cell] = r
    return g


def matrix(cells, value):
    reps = sorted({c[0] for c in cells})
    inner = sorted({c[1] for c in cells}, key=lambda v: (len(v), v))
    if len(cells) != len(reps) * len(inner):
        raise InputError("incomplete repeat by fold grid")
    try:
        a = np.array([[float(cells[(r, i)][value]) for i in inner] for r in reps])
    except ValueError:
        raise InputError(f"non-numeric {value} value")
    if not np.isfinite(a).all() or a.min() < 0 or a.max() > 1:
        raise InputError(f"{value} values must be finite numbers between 0 and 1")
    return reps, inner, a


def run(folds_path, oof_path=None, limits=None, seed=2026, b=10000, b_patient=2000):
    fg = grid(read(folds_path, "auroc"), "fold")
    og = grid(read(oof_path, "probability"), "patient_id") if oof_path else {}
    grids = {tuple(map(tuple, matrix(c, "auroc")[:2])) for c in fg.values()}
    if len(grids) != 1:
        raise InputError("all models and conditions must share the same repeat and fold ids")
    reps0, folds0 = grids.pop()
    n_rep, n_fold = len(reps0), len(folds0)
    oof = {}
    y = None
    for k, cells in og.items():
        reps, pats, p = matrix(cells, "probability")
        try:
            labs = np.array([[int(cells[(r, q)]["label"]) for q in pats] for r in reps])
        except ValueError:
            raise InputError(f"{k}: labels must be integers 0 or 1")
        if not set(np.unique(labs)) <= {0, 1}:
            raise InputError(f"{k}: labels must be 0 or 1")
        if not (labs == labs[0]).all():
            raise InputError(f"{k}: a patient's label differs across repeats")
        lab = labs[0]
        if y is None:
            y, pat_ids, oof_reps = lab, pats, reps
        elif pats != pat_ids or reps != oof_reps or not np.array_equal(lab, y):
            raise InputError(f"{k}: patients, repeats or labels differ from other models")
        oof[k] = p
    _, rep_idx, pat_idx = resample_indices(seed, n_rep, n_fold, len(y) if y is not None else None, b, b_patient)

    def patient_boot(p):
        return np.array([np.nanmean([auroc(y[i], p[r][i]) for r in range(p.shape[0])]) for i in pat_idx])

    entries, solo_lower = [], defaultdict(list)
    for (model, layer, cond), cells in sorted(fg.items()):
        if cond != "solo":
            continue
        a = matrix(cells, "auroc")[2]
        rep = a.mean(axis=1)
        lo, hi = percentile_ci(rep[rep_idx].mean(axis=1))
        extra = {"interval": "bootstrap over repeat means"}
        if (model, layer, cond) in oof:
            plo, phi = percentile_ci(patient_boot(oof[(model, layer, cond)]))
            extra.update({"patient_lower_95": plo, "patient_upper_95": phi})
            solo_lower[layer].append(plo)
        else:
            solo_lower[layer].append(lo)
        entries.append(entry("solo_layer_auroc", f"held-out AUROC of {layer} alone, mean over {n_rep}x{n_fold} folds",
                             float(a.mean()), lo, hi, [model, layer], limits, extra=extra))
    weak = sorted(l for l, v in solo_lower.items() if max(v) <= 0.5)
    flags = [{"flag": "layer_not_above_chance", "components": [l],
              "rule": "no solo held-out AUROC interval for this layer lies above 0.5",
              "wording": "held-out performance does not exceed chance"} for l in weak]
    for model, layer in sorted({(m, l) for m, l, c in fg if c == "with"}):
        if (model, layer, "without") not in fg:
            raise InputError(f"{model} {layer}: 'with' rows have no matching 'without' rows")
        aw = matrix(fg[(model, layer, "with")], "auroc")[2]
        ao = matrix(fg[(model, layer, "without")], "auroc")[2]
        loss = (ao - aw).mean(axis=1)
        lo, hi = percentile_ci(loss[rep_idx].mean(axis=1))
        extra = {"auroc_with": float(aw.mean()), "auroc_without": float(ao.mean()),
                 "auroc_change_with_minus_without": float((aw - ao).mean()),
                 "interval": "paired bootstrap over repeat means"}
        kw, ko = (model, layer, "with"), (model, layer, "without")
        if kw in oof and ko in oof:
            d = patient_boot(oof[ko]) - patient_boot(oof[kw])
            extra.update({"patient_loss_mean": float(np.nanmean(d)),
                          "patient_lower_95": percentile_ci(d)[0], "patient_upper_95": percentile_ci(d)[1]})
        entries.append(entry("auroc_loss_from_adding_layer", f"{model}: AUROC without {layer} minus with {layer}",
                             float((ao - aw).mean()), lo, hi, [model, layer], limits, extra=extra))
        gain_hi = extra.get("patient_upper_95", hi)
        if layer in weak and gain_hi < 0:
            flags.append({"flag": "gain_only_with_chance_level_layer", "components": [model, layer],
                          "rule": "AUROC rises when a layer flagged as not above chance is added"})
    notes = [f"bootstrap seed {seed}, {b} repeat resamples, {b_patient if oof else 0} patient resamples",
             "folds within a repeat share training patients, so intervals are optimistic about new patients",
             "decisions use the interval over repeat means; flags use the patient interval when out-of-fold predictions are given"]
    return report("layers", [p for p in (folds_path, oof_path) if p], entries, flags, notes)
