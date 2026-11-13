import csv, json, sys
from pathlib import Path

SRC = Path.home() / "sgof-camera-ready" / "results" / "public"
OUT = Path(__file__).resolve().parent / "data"
FUSION = {"naive": "naive_concatenation", "sgof": "sgof", "mogonet_style": "mogonet_style_reimplementation", "mlp_late": "mlp_late_fusion"}
SOLO = {"single_0": "mRNA", "single_1": "DNAm", "single_2": "miRNA"}

for ds in ("rosmap", "brca"):
    d = json.loads((SRC / f"public_{ds}.json").read_text())
    m = d["meta"]
    assert d["complete"] and not m["smoke"] and m["n_repeats"] == 5 and m["n_splits"] == 5
    assert m["layers"] == ["mRNA", "DNAm", "miRNA"]
    rows = []
    for rep in range(5):
        r = d["repeats"][str(rep)]
        for key, name in FUSION.items():
            for cond, src in (("with", "noise"), ("without", "real")):
                a = r[src][key]["auroc"]
                assert len(a) == 5
                rows += [[name, "noise", cond, rep, k, f"{a[k]:.6f}"] for k in range(5)]
        for key, layer in SOLO.items():
            a = r["real"][key]["auroc"]
            rows += [["single_layer_gcn", layer, "solo", rep, k, f"{a[k]:.6f}"] for k in range(5)]
        a = r["noise"]["single_noise"]["auroc"]
        rows += [["single_layer_gcn", "noise", "solo", rep, k, f"{a[k]:.6f}"] for k in range(5)]
    with open(OUT / f"{ds}_fold_auroc.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model_id", "layer", "condition", "repeat", "fold", "auroc"])
        w.writerows(rows)
    print(ds, len(rows))
